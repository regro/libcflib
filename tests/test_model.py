import json
import os

from libcflib.model import Node


def test_node(tmpdir):
    d = {'a': 'hi', 'world': 'python'}
    with open(os.path.join(tmpdir, 'a.json'), 'w') as f:
        json.dump(d, f)

    n = Node(name='a', folder=tmpdir)
    assert n.a == 'hi'
    assert n['a'] == 'hi'
