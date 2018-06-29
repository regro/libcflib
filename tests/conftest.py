import sys
import shutil
import builtins
import subprocess

import pytest


def rmtree(dirname):
    """Remove a directory, even if it has read-only files (Windows).
    Git creates read-only files that must be removed on teardown. See
    https://stackoverflow.com/questions/2656322  for more info.

    Parameters
    ----------
    dirname : str
        Directory to be removed
    """
    try:
        shutil.rmtree(dirname)
    except PermissionError:
        if sys.platform == "win32":
            subprocess.check_call(["del", "/F/S/Q", dirname], shell=True)
        else:
            raise


@pytest.fixture
def gitecho():
    aliases = builtins.aliases
    orig_alias = aliases.get("git", None)
    aliases["git"] = lambda args: "Would have run: " + " ".join(args) + "\n"
    yield None
    if orig_alias is None:
        del aliases["git"]
    else:
        aliases["git"] = orig_alias


@pytest.fixture
def tmpgraphdir(tmpdir_factory, gitecho):
    env = builtins.__xonsh_env__
    d = tmpdir_factory.mktemp("graph", numbered=False)
    d.mkdir("artifacts").mkdir("mypkg").mkdir("/somechannel").mkdir("noarch")
    orig_libcfgraph_dir = env.get("LIBCFGRAPH_DIR")
    env["LIBCFGRAPH_DIR"] = d
    yield d
    rmtree(d)
    env["LIBCFGRAPH_DIR"] = orig_libcfgraph_dir
