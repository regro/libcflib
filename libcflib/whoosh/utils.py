"""Tools for using whoosh."""
import os.path

from whoosh.index import exists_in
from whoosh.filedb.filestore import FileStorage
from whoosh.fields import TEXT, KEYWORD, BOOLEAN, NUMERIC
from libcflib.whoosh.fields import DICT, NestedSchema
from libcflib.whoosh.index import NestedIndex


TYPE_MAP = {
    "string": TEXT,
    "list": KEYWORD,
    "set": KEYWORD,
    "bool": BOOLEAN,
    "float": NUMERIC(numtype=float),
    "integer": NUMERIC,
    "dict": DICT,
}


def create_whoosh_schema(schema):
    """Create a whoosh schema from a cerberus schema.

    Parameters
    ----------
    schema : dict
        A cerberus schema.

    Returns
    -------
    libcflib.fields.NestedSchema
        A whoosh schema with the same structure as the input.
    """
    fields = {k: TYPE_MAP[v["type"]] for k, v in schema.items()}
    for f, t in fields.items():
        try:
            fields[f] = t(schema=schema[f]["schema"], type_map=TYPE_MAP)
        except (TypeError, KeyError):
            fields[f] = t()
        fields[f].stored = True
    return NestedSchema(**fields)


def get_index(index, schema=None):
    """Open or create a whoosh index.

    Opens a whoosh index with the specified name and schema.
    If there is no index with the specified name, a new index is created.

    Parameters
    ----------
    index : str
        The name of the index.
    schema : whoosh.fields.Schema
        The schema to use for the index.

    Returns
    -------
    libcflib.index.NestedIndex
        A whoosh index with the specified name and schema.
    """
    indexname = "MAIN"
    storage = FileStorage(index)
    if not os.path.exists(index):
        os.mkdir(index)
    if exists_in(index):
        return NestedIndex(storage, schema=schema, indexname=indexname)
    else:
        return NestedIndex.create(storage, schema, indexname)


def add(index, schema=None, **kwargs):
    """Add a document to an index.

    Parameters
    ----------
    index : str
        The name of the index.
    schema : whoosh.index.Schema
        The schema to use for the index.
    **kwargs
        Fields and values of the document to add.
    """
    ix = get_index(index, schema)
    writer = ix.writer()
    writer.add_document(**kwargs)
    writer.commit()


def add_from(index, docs, schema=None):
    """Add multiple documents to an index.

    Parameters
    ----------
    index : str
        The name of the index.
    docs : list of dict
        The documents to add.
    schema : whoosh.index.Schema
        The schema to use for the index.
    """
    ix = get_index(index, schema)
    writer = ix.writer()
    for doc in docs:
        doc = {k: v for k, v in doc.items() if k in ix.schema.names()}
        writer.add_document(**doc)
    writer.commit()


def search(index, query):
    """Search an index.

    Parameters
    ----------
    index : str
        The name of the index.
    query : dict
        The query.

    Returns
    -------
    list of dict
        A list of the results matching the query.
    """
    ix = get_index(index)
    with ix.searcher() as searcher:
        return [dict(res) for res in searcher.documents(**query)]
