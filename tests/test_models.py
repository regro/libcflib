import os
import json
import builtins

from libcflib.models import Artifact, Package


def test_artifact(tmpgraphdir):
    d = {"a": "hi", "world": "python"}
    art_dir = os.path.join(tmpgraphdir, "artifacts", "mypkg", "somechannel", "noarch")
    with open(os.path.join(art_dir, "mypkg.json"), "w") as f:
        json.dump(d, f)

    env = builtins.__xonsh__.env
    env["LIBCFGRAPH_DIR"] = tmpgraphdir
    pkg, channel, arch = art_dir.split("/")[-3:]
    n = Artifact(pkg=pkg, channel=channel, arch=arch, name="mypkg")
    assert n.a == "hi"
    assert n["a"] == "hi"
    # test asdict
    exp = d.copy()
    exp["spec"] = {
        "arch": "noarch",
        "channel": "somechannel",
        "name": "mypkg",
        "path": "mypkg/somechannel/noarch/mypkg.json",
        "pkg": "mypkg",
    }
    assert exp == n.asdict()
    # make sure we can hash artifacts
    hash(n)


def test_package(tmpgraphdir):
    p = Package(name="mypkg")
    exp = {"arches": set(), "artifacts": {}, "channels": set(), "name": "mypkg"}
    obs = p.asdict()
    assert exp == obs


# TODO: test feedstock
