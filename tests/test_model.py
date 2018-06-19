import json
import os

from libcflib.model import Artifact


def test_node(tmpdir):
    d = {"a": "hi", "world": "python"}
    with open(os.path.join(tmpdir, "a.json"), "w") as f:
        json.dump(d, f)

    n = Artifact(tmpdir, "a")
    assert n.a == "hi"
    assert n["a"] == "hi"
