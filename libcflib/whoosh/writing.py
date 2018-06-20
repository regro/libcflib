# Copyright 2007 Matt Chaput. All rights reserved.
"""Custom whoosh writers."""
from whoosh.util.text import utf8encode
from whoosh.writing import SegmentWriter


def get_value(fields, fieldname):
    """Get the value of a field from a nested dict.

    Parameters
    ----------
    fields : dict
        The nested dict.
    fieldname : str
        The name of the field. For nested fields, the name is of the form
        `a.b.c`, which corresponds to `fields['a']['b']['c']`.

    Returns
    -------
    The value.
    """

    keys = fieldname.split(".")
    value = fields
    for k in keys:
        if value is None:
            return
        value = value.get(k)
    return value


def get_fieldnames(fields, base=""):
    """Get the names of the fields in a nested dict.

    Parameters
    ----------
    fields : dict
        The nested dict.
    base : str
        A string that is added to the beginning of the returned field names.

    Yields
    ------
    str
        The name of a field in `fields`. For the nested field
        `fields['a']['b']['c']` the name is `a.b.c`.
    """

    try:
        for name, value in fields.items():
            if name.startswith("_"):
                continue
            base += name + "."
            for fn in get_fieldnames(value, base):
                yield fn
            base = base[:-2]
    except AttributeError:
        base = base[:-1]
        yield base
        base = base[:-1]


class NestedWriter(SegmentWriter):
    """An IndexWriter that writes to a NestedIndex."""

    def add_document(self, **fields):
        self._check_state()
        perdocwriter = self.perdocwriter
        schema = self.schema
        docnum = self.docnum
        add_post = self.pool.add

        docboost = self._doc_boost(fields)
        fieldnames = sorted(list(get_fieldnames(fields)))
        self._check_fields(schema, fieldnames)

        perdocwriter.start_doc(docnum)
        for fieldname in fieldnames:
            value = get_value(fields, fieldname)
            if value is None:
                continue
            field = schema[fieldname]

            length = 0
            if field.indexed:
                # TODO: Method for adding progressive field values, ie
                # setting start_pos/start_char?
                fieldboost = self._field_boost(fields, fieldname, docboost)
                # Ask the field to return a list of (text, weight, vbytes)
                # tuples
                items = field.index(value)
                # Only store the length if the field is marked scorable
                scorable = field.scorable
                # Add the terms to the pool
                for tbytes, freq, weight, vbytes in items:
                    weight *= fieldboost
                    if scorable:
                        length += freq
                    add_post((fieldname, tbytes, docnum, weight, vbytes))

            if field.separate_spelling():
                spellfield = field.spelling_fieldname(fieldname)
                for word in field.spellable_words(value):
                    word = utf8encode(word)[0]
                    # item = (fieldname, tbytes, docnum, weight, vbytes)
                    add_post((spellfield, word, 0, 1, vbytes))

            vformat = field.vector
            if vformat:
                analyzer = field.analyzer
                # Call the format's word_values method to get posting values
                vitems = vformat.word_values(value, analyzer, mode="index")
                # Remove unused frequency field from the tuple
                vitems = sorted(
                    (text, weight, vbytes) for text, _, weight, vbytes in vitems
                )
                perdocwriter.add_vector_items(fieldname, field, vitems)

            # Allow a custom value for stored field/column
            customval = fields.get("_stored_%s" % fieldname, value)

            # Add the stored value and length for this field to the per-
            # document writer
            sv = customval if field.stored else None
            perdocwriter.add_field(fieldname, field, sv, length)

            column = field.column_type
            if column and customval is not None:
                cv = field.to_column_value(customval)
                perdocwriter.add_column_value(fieldname, column, cv)

        perdocwriter.finish_doc()
        self._added = True
        self.docnum += 1
