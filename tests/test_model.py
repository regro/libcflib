import os
import json
import builtins

from libcflib.model import Artifact


def test_node(tmppkgdir):
    d = {"a": "hi", "world": "python"}
    with open(os.path.join(tmppkgdir, "a.json"), "w") as f:
        json.dump(d, f)

    env = builtins.__xonsh_env__
    dirs = str(tmppkgdir).split("/")
    env["LIBCFGRAPH_DIR"] = "/".join(dirs[:-3])
    pkg, channel, arch = dirs[-3:]
    n = Artifact(pkg=pkg, channel=channel, arch=arch, name="a")
    assert n.a == "hi"
    assert n["a"] == "hi"
