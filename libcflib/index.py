from whoosh.index import FileIndex


class NestedIndex(FileIndex):
    def writer(self, procs=1, **kwargs):
        from libcflib.writing import NestedWriter

        return NestedWriter(self, **kwargs)
