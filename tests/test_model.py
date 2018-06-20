import os
import json
import builtins

from libcflib.model import Artifact


def test_node(tmppkgdir):
    d = {"a": "hi", "world": "python"}
    pkg_path = os.path.join(tmppkgdir, 'mypkg', 'somechannel', 'noarch', "mypkg.json")
    with open(pkg_path, "w") as f:
        json.dump(d, f)

    env = builtins.__xonsh_env__
    dirs = str(pkg_path).split("/")
    env["LIBCFGRAPH_DIR"] = "/".join(dirs[:-5])
    print(env["LIBCFGRAPH_DIR"])
    pkg, channel, arch, _ = dirs[-4:]
    n = Artifact(pkg=pkg, channel=channel, arch=arch, name="mypkg")
    assert n.a == "hi"
    assert n["a"] == "hi"
    # test asdict
    assert d == n.asdict()
    # make sure we can hash artifacts
    hash(n)
