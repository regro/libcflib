"""Custom whoosh indexes."""
from whoosh.index import FileIndex


class NestedIndex(FileIndex):
    """
    An Index that contains documents with nested structure. When a nested
    dictionary is added to this index, the correct keys are extracted.
    """

    def writer(self, procs=1, **kwargs):
        from libcflib.whoosh.writing import NestedWriter

        return NestedWriter(self, **kwargs)
