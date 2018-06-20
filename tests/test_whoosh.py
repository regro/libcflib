import os.path

from libcflib.whooshutils import create_whoosh_schema, add, search


def test_search(tmpdir):
    schema = {
        "a": {"type": "string"},
        "b": {"type": "integer"},
        "c": {
            "type": "dict",
            "schema": {
                "a": {"type": "string"},
                "d": {
                    "type": "dict",
                    "schema": {"e": {"type": "integer"}, "f": {"type": "string"}},
                },
                "e": {"type": "float"},
            },
        },
    }
    ws = create_whoosh_schema(schema)

    index = os.path.join(tmpdir, "index")
    doc = {
        "a": "hello",
        "b": 3,
        "c": {"a": "world", "d": {"e": 5, "f": "hi"}, "e": 3.5},
    }
    add(index, ws, **doc)

    query = {"c.a": "world", "c.d.e": 5, "c.e": 3.5}
    results = search(index, query)
    assert results == {
        "a": "hello",
        "b": 3,
        "c.a": "world",
        "c.d.e": 5,
        "c.d.f": "hi",
        "c.e": 3.5,
    }
