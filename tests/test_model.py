import os
import json
import builtins

from libcflib.model import Artifact


def test_artifact(tmpgraphdir):
    d = {"a": "hi", "world": "python"}
    art_dir = os.path.join(tmpgraphdir, 'artifacts', 'mypkg', 'somechannel', 'noarch')
    with open(os.path.join(art_dir, "mypkg.json"), "w") as f:
        json.dump(d, f)

    env = builtins.__xonsh_env__
    env["LIBCFGRAPH_DIR"] = tmpgraphdir
    pkg, channel, arch = art_dir.split('/')[-3:]
    n = Artifact(pkg=pkg, channel=channel, arch=arch, name="mypkg")
    assert n.a == "hi"
    assert n["a"] == "hi"
    # test asdict
    assert d == n.asdict()
    # make sure we can hash artifacts
    hash(n)

# TODO: test package
# TODO: test feedstock
