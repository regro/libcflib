"""Custom whoosh indexes."""
from whoosh.index import FileIndex


class NestedIndex(FileIndex):
    """A whoosh index that uses a NestedWriter to add documents with a nested structure."""

    def writer(self, procs=1, **kwargs):
        from libcflib.writing import NestedWriter

        return NestedWriter(self, **kwargs)
