import os.path

from whoosh.index import open_dir, exists_in, create_in
from libcflib.fields import TYPE_MAP, NestedSchema


def create_whoosh_schema(schema):
    fields = {k: TYPE_MAP[v['type']] for k, v in schema.items()}
    return NestedSchema(**fields)


def get_index(index, schema):
    if not os.path.exists(index):
        os.mkdir(index)
    if exists_in(index):
        return open_dir(index)
    else:
        return create_in(index, schema)


def add(index, **kwargs):
    ix = get_index(index)
    writer = ix.writer()
    doc = {k: v for k, v in kwargs.items() if k in ix.schema.names()}
    writer.add_document(**doc)
    writer.commit()


def add_from(index, docs):
    ix = get_index(index)
    writer = ix.writer()
    for doc in docs:
        doc = {k: v for k, v in doc.items() if k in ix.schema.names()}
        writer.add_document(**doc)
    writer.commit()


def search(index, **kwargs):
    ix = get_index(index)
    with ix.searcher() as searcher:
        return searcher.document(**kwargs)
