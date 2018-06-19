from collections.abc import MutableMapping, Sequence


PY_TO_CERB = {int: "integer", str: "string", float: "float", set: "set", bool: "bool"}


def recursive_schema(d):
    schema = {}
    for k, v in d.items():
        if isinstance(v, MutableMapping):
            schema[k] = {"type": "dict", "schema": recursive_schema(v)}
        elif isinstance(v, Sequence):
            schema[k] = {
                "type": "list",
                "schema": {"type": PY_TO_CERB[type(next(iter(v)))]},
            }
        else:
            schema[k] = {"type": PY_TO_CERB[type(v)]}
    return schema
