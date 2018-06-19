from whoosh.fields import (FieldType, TEXT, KEYWORD, BOOLEAN, NUMERIC)


TYPE_MAP = {'string': TEXT,
            'list': KEYWORD,
            'set': KEYWORD,
            'bool': BOOLEAN,
            'integer': NUMERIC}


class DICT(FieldType):
    type_map = TYPE_MAP

    def __init__(self, schema, stored=False):
        self.schema = schema
        self.type_map['dict'] = DICT

    def subfields(self):
        for k, v in self.schema.items():
            try:
                subfield = self.type_map[v['type']](schema=v['schema'], stored=self.stored)
            except (TypeError, NameError):
                subfield = self.type_map[v['type']](stored=self.stored)
            yield k, subfield


TYPE_MAP['dict'] = DICT
