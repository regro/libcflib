"""Standard fixie tools for dealing with JSON."""
import json
import uuid
import base64
from collections.abc import Set


def default(obj):
    """For custom object serialization."""
    if hasattr(obj, "asdict"):
        return obj.asdict()
    elif isinstance(obj, Set):
        return {"__set__": True, "elements": sorted(obj)}
    elif isinstance(obj, bytes):
        return {
            "__bytes__": "base64",
            "value": base64.standard_b64encode(obj).decode("utf-8"),
        }
    elif isinstance(obj, uuid.UUID):
        return {"__UUID__": True, "value": str(obj)}
    raise TypeError(repr(obj) + " is not JSON serializable")


def object_hook(dct):
    """For custom object deserialization."""
    if "__set__" in dct:
        return set(dct["elements"])
    elif "__bytes__" in dct:
        return base64.standard_b64decode(dct["value"].encode("utf-8"))
    elif "__UUID__" in dct:
        return uuid.UUID(dct["value"])
    return dct


def dumps(obj, sort_keys=True, separators=(",", ":"), default=default, **kwargs):
    """Returns a JSON string from a Python object."""
    return json.dumps(
        obj, sort_keys=sort_keys, separators=separators, default=default, **kwargs
    )


def dump(obj, fp, sort_keys=True, separators=(",", ":"), default=default, **kwargs):
    """Returns a JSON string from a Python object."""
    return json.dump(
        obj, fp, sort_keys=sort_keys, separators=separators, default=default, **kwargs
    )


def encode(obj, **kwargs):
    """Encodes JSON with forward slash encoding, such as in Tornado."""
    return dumps(obj, **kwargs).replace("</", "<\\/")


def appendline(obj, f, **kwargs):
    """Appends a line to a line-oriented JSON file (either str path or file handle)."""
    if isinstance(f, str):
        with open(f, "a+") as fp:
            dump(obj, fp, **kwargs)
            fp.write("\n")
    else:
        dump(obj, f, **kwargs)
        f.write("\n")


def loads(s, object_hook=object_hook, **kwargs):
    """Loads a string as JSON, with approriate object hooks"""
    return json.loads(s, object_hook=object_hook, **kwargs)


def load(fp, object_hook=object_hook, **kwargs):
    """Loads a file object as JSON, with appropriate object hooks."""
    return json.load(fp, object_hook=object_hook, **kwargs)


def decode(s, **kwargs):
    if hasattr(s, "decode"):
        # handle bytes, if needed
        s = s.decode("utf-8")
    return loads(s, **kwargs)


def loadlines(f, **kwargs):
    """Loads lines from a file (either str path of file handle)."""
    if isinstance(f, str):
        with open(f) as fp:
            lines = [loads(line, **kwargs) for line in fp]
    else:
        lines = [loads(line, **kwargs) for line in f]
    return lines
