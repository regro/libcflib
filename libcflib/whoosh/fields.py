# Copyright 2007 Matt Chaput. All rights reserved.
"""Custom whoosh field types and schemas."""
import sys
import re
import fnmatch

from whoosh.fields import FieldType, Schema, FieldConfigurationError


class DICT(FieldType):
    """
    Special field type that lets you index dictionaries.
    The field converts the dict to separate keys for each field before indexing.
    """

    def __init__(self, schema, type_map, stored=False):
        """Initialize a DICT.

        Parameters
        ----------
        schema : dict
            The schema for this object.
        type_map : dict
            A mapping from python types to whoosh FieldTypes.
        """
        self.schema = schema
        self.type_map = type_map
        self.stored = stored

    def subfields(self):
        for k, v in self.schema.items():
            subfield = self.type_map[v["type"]]
            if type(subfield) is type:
                try:
                    subfield = self.type_map[v["type"]](
                        schema=v["schema"], type_map=self.type_map
                    )
                except (TypeError, KeyError):
                    subfield = self.type_map[v["type"]]()
            subfield.stored = self.stored
            yield k, subfield


class NestedSchema(Schema):
    """A schema for nested documents."""

    def __init__(self, **fields):
        super().__init__(**fields)

    def add(self, name, fieldtype, glob=False):
        # If the user passed a type rather than an instantiated field object,
        # instantiate it automatically
        if type(fieldtype) is type:
            try:
                fieldtype = fieldtype()
            except Exception:
                e = sys.exc_info()[1]
                raise FieldConfigurationError(
                    "Error: %s instantiating field " "%r: %r" % (e, name, fieldtype)
                )

        if not isinstance(fieldtype, FieldType):
            raise FieldConfigurationError("%r is not a FieldType object" % fieldtype)

        self._subfields[name] = sublist = []
        for suffix, subfield in fieldtype.subfields():
            fname = name + "." + suffix if suffix else name
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
