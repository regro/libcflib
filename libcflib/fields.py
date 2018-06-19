from whoosh.fields import (FieldType, TEXT, KEYWORD, BOOLEAN, NUMERIC)


TYPE_MAP = {'string': TEXT,
            'list': KEYWORD,
            'set': KEYWORD,
            'bool': BOOLEAN,
            'integer': NUMERIC,
            'dict': DICT}


class DICT(FieldType):
    def __init__(self, schema, stored=False):
        self.schema = schema

    def subfields(self):
        for k, v in self.schema.items():
            try:
                subfield = TYPE_MAP[v['type']](schema=v['schema'], stored=self.stored)
            except (TypeError, NameError):
                subfield = TYPE_MAP[v['type']](stored=self.stored)
            yield k, subfield
