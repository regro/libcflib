import os
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


@pytest.fixture(scope="session")
def gitecho():
    aliases = builtins.aliases
    orig_alias = aliases.get("git", None)
    aliases["git"] = lambda args: "Would have run: " + " ".join(args) + "\n"
    yield None
    if orig_alias is None:
        del aliases["git"]
    else:
        aliases["git"] = orig_alias


@pytest.fixture(scope="session")
def tmpgraphdir(tmpdir_factory, gitecho):
    env = builtins.__xonsh__.env
    d = tmpdir_factory.mktemp("graph", numbered=False)
    pkg = d.mkdir("artifacts").mkdir("mypkg")
    pkg.mkdir("somechannel").mkdir("noarch")
    pkg.mkdir("otherchannel").mkdir("linux-64")
    orig_libcfgraph_dir = env.get("LIBCFGRAPH_DIR")
    orig_libcfgraph_index = env.get("LIBCFGRAPH_INDEX")
    ix = d.mkdir("index")
    env["LIBCFGRAPH_DIR"] = d
    env["LIBCFGRAPH_INDEX"] = os.path.join(ix)
    yield d
    rmtree(d)
    env["LIBCFGRAPH_DIR"] = orig_libcfgraph_dir
    env["LIBCFGRAPH_INDEX"] = orig_libcfgraph_index


@pytest.fixture(scope="session")
def documents():
    return [
        {
            "path": os.path.join("mypkg", "somechannel", "noarch", "pkg_0.json"),
            "pkg": "mypkg",
            "channel": "somechannel",
            "arch": "noarch",
            "name": "pkg_0",
            "a": 3,
            "b": 5,
            "c": 3,
        },
        {
            "path": os.path.join("mypkg", "somechannel", "noarch", "pkg_1.json"),
            "pkg": "mypkg",
            "channel": "somechannel",
            "arch": "noarch",
            "name": "pkg_1",
            "a": 3,
            "b": 2,
            "c": 8,
        },
        {
            "path": os.path.join("mypkg", "otherchannel", "linux-64", "pkg.json"),
            "pkg": "mypkg",
            "channel": "otherchannel",
            "arch": "linux-64",
            "name": "pkg",
            "a": 4,
            "b": 2,
            "c": 9,
        },
    ]
