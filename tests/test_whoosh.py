import os.path

from libcflib.whoosh.utils import create_whoosh_schema, add, search


def test_search(tmpdir):
    schema = {
        "a": {"type": "string", "stored": True},
        "b": {"type": "integer", "stored": True},
        "c": {
            "type": "dict",
            "schema": {
                "a": {"type": "string", "stored": True},
                "d": {
                    "type": "dict",
                    "schema": {"e": {"type": "integer"}, "f": {"type": "string"}},
                    "stored": True,
                },
                "e": {"type": "float", "stored": False},
            },
            "stored": True,
        },
    }
    ws = create_whoosh_schema(schema)

    index = os.path.join(tmpdir, "index")
    doc = {
        "a": "hello",
        "b": 3,
        "c": {"a": "world", "d": {"e": 5, "f": "hi"}, "e": 3.5},
    }
    add(index, schema=ws, **doc)

    query = {"c.a": "world", "c.d.e": 5, "c.e": 3.5}
    results = search(index, query)
    assert results == [
        {"a": "hello", "b": 3, "c.a": "world", "c.d.e": 5, "c.d.f": "hi"}
    ]
