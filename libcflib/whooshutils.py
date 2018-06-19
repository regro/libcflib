import os.path
from whoosh.index import open_dir, exists_in, create_in
from whoosh.qparser import QueryParser
from whoosh.fields import (Schema, TEXT, KEYWORD, BOOLEAN, NUMERIC, STORED,
                           ID)


SCHEMA = Schema(name=ID(stored=True),
                archived=BOOLEAN,
                bad=TEXT,
                harvest_time=NUMERIC,
                req=KEYWORD,
                versions=KEYWORD,
                PRed=STORED,
                artifacts=STORED)


def get_index(index):
    if not os.path.exists('index'):
        os.mkdir('index')
    if exists_in(index):
        return open_dir(index)
    else:
        return create_index(index)


def create_index(index, schema=SCHEMA):
    ix = create_in(index, schema)
    return ix


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
