import os.path

from whoosh.index import exists_in
from libcflib.fields import TYPE_MAP, NestedSchema
from libcflib.index import NestedIndex


def create_whoosh_schema(schema):
    fields = {k: TYPE_MAP[v["type"]] for k, v in schema.items()}
    for f, t in fields.items():
        try:
            fields[f] = t(schema=schema[f]["schema"], stored=True)
        except (TypeError, KeyError):
            fields[f] = t(stored=True)
        fields[f].stored = True
    return NestedSchema(**fields)


def get_index(index, schema=None):
    from whoosh.filedb.filestore import FileStorage

    indexname = "MAIN"
    storage = FileStorage(index)
    if not os.path.exists(index):
        os.mkdir(index)
    if exists_in(index):
        return NestedIndex(storage, schema=schema, indexname=indexname)
    else:
        return NestedIndex.create(storage, schema, indexname)


def add(index, schema=None, **kwargs):
    ix = get_index(index, schema)
    writer = ix.writer()
    writer.add_document(**kwargs)
    writer.commit()


def add_from(index, docs, schema=None):
    ix = get_index(index, schema)
    writer = ix.writer()
    for doc in docs:
        doc = {k: v for k, v in doc.items() if k in ix.schema.names()}
        writer.add_document(**doc)
    writer.commit()


def search(index, query):
    ix = get_index(index)
    with ix.searcher() as searcher:
        return searcher.document(**query)
