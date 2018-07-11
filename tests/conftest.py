import os
import sys
import shutil
import builtins
import subprocess

import pytest
from whoosh import index
from whoosh.fields import Schema, NUMERIC

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
    env = builtins.__xonsh_env__
    d = tmpdir_factory.mktemp("graph", numbered=False)
    d.mkdir("artifacts").mkdir("mypkg").mkdir("/somechannel").mkdir("noarch")
    ix = d.mkdir("whoosh")
    orig_libcfgraph_dir = env.get("LIBCFGRAPH_DIR")
    orig_libcfgraph_index = env.get("LIBCFGRAPH_INDEX")
    env["LIBCFGRAPH_DIR"] = d
    env["LIBCFGRAPH_INDEX"] = os.path.join(ix)
    yield d
    rmtree(d)
    env["LIBCFGRAPH_DIR"] = orig_libcfgraph_dir
    env["LIBCFGRAPH_INDEX"] = orig_libcfgraph_index


@pytest.fixture(scope="session")
def documents():
    return [
            {'a':3, 'b':5, 'c':3},
            {'a':3, 'b':2, 'c':8},
            {'a':4, 'b':2, 'c':9},
           ]

@pytest.fixture(scope="session")
def tmpgraphindex(tmpgraphdir, documents):
    schema = Schema(a=NUMERIC, b=NUMERIC, c=NUMERIC)
    ix = index.create_in(os.path.join(tmpgraphdir, 'whoosh'), schema, 'ARTIFACTS')
    writer = ix.writer()
    for doc in documents:
        writer.add_document(**doc)
    writer.commit()
    yield ix
