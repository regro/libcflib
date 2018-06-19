# Copyright 2007 Matt Chaput. All rights reserved.
import sys
import re
import fnmatch

from whoosh.fields import (
    FieldType,
    Schema,
    FieldConfigurationError,
    TEXT,
    KEYWORD,
    BOOLEAN,
    NUMERIC,
)


TYPE_MAP = {
    'string': TEXT,
    'list': KEYWORD,
    'set': KEYWORD,
    'bool': BOOLEAN,
    'float': NUMERIC(numtype=float),
    'integer': NUMERIC,
}


class DICT(FieldType):
    type_map = TYPE_MAP

    def __init__(self, schema, stored=False):
        self.schema = schema
        self.type_map['dict'] = DICT

    def subfields(self):
        for k, v in self.schema.items():
            try:
                subfield = self.type_map[v['type']](
                    schema=v['schema'], stored=self.stored
                )
            except (TypeError, KeyError):
                subfield = self.type_map[v['type']](stored=self.stored)
            yield k, subfield


TYPE_MAP['dict'] = DICT


class NestedSchema(Schema):
    def __init__(self, **fields):
        super().__init__(**fields)

    def add(self, name, fieldtype, glob=False):
        # If the user passed a type rather than an instantiated field object,
        # instantiate it automatically
        if type(fieldtype) is type:
            try:
                fieldtype = fieldtype()
            except:
                e = sys.exc_info()[1]
                raise FieldConfigurationError(
                    "Error: %s instantiating field " "%r: %r" % (e, name, fieldtype)
                )

        if not isinstance(fieldtype, FieldType):
            raise FieldConfigurationError("%r is not a FieldType object" % fieldtype)

        self._subfields[name] = sublist = []
        for suffix, subfield in fieldtype.subfields():
            fname = name + '.' + suffix if suffix else name
            sublist.append(fname)

            # Check field name
            if fname.startswith("_"):
                raise FieldConfigurationError("Names cannot start with _")
            elif " " in fname:
                raise FieldConfigurationError("Names cannot contain spaces")
            elif fname in self._fields or (glob and fname in self._dyn_fields):
                raise FieldConfigurationError("%r already in schema" % fname)

            # Add the field
            if isinstance(subfield, DICT):
                self.add(fname, subfield)
                continue
            if glob:
                expr = re.compile(fnmatch.translate(name))
                self._dyn_fields[fname] = (expr, subfield)
            else:
                subfield.on_add(self, fname)
                self._fields[fname] = subfield
