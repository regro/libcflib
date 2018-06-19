"""Database for accessing graph information"""
import os

import zict

from libcflib.model import Artifact


class DB:
    """A logging object for fixie that stores information in line-oriented JSON
    format.
    """

    __inst = None

    def __new__(cls):
        # make the db a singleton
        if DB.__inst is None:
            DB.__inst = object.__new__(cls)
        return DB.__inst

    def __init__(self, cache_size=1e6):
        """

        Parameters
        ----------
        cache_size : int
            Size of the cache

        Caching forked from Streamz
        Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        All rights reserved.

        """
        if os.path.exists($LIBCFGRAPH_DIR):
            git pull $LIBCFGRAPH_URL master
        else:
            git clone $LIBCFGRAPH_URL $LIBCFGRAPH_DIR --depth 1
        self.cache = {}
        self.lru = zict.LRU(cache_size, self.cache)

    def _build_whoosh(self):
        self.idx = 'whoosh'


    def search(self, **kwargs):
        """Search the database

        Parameters
        ----------
        kwargs : dict
            The keys to search on

        Yields
        -------
        res :
            The loaded artifact search results

        Caching forked from Streamz
        Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        All rights reserved.
        """
        with self.idx.searcher() as searcher:
            results = searcher.search()
            for result in results:
                if result not in self.cache:
                    data = self.get_data(result)
                    self.cache[result] = data
                else:
                    data = self.cache[results]
                yield data

    def get_data(self, data):
        """Get the artifact data from the database

        Parameters
        ----------
        data : tuple
            data for loading the artifact

        Returns
        -------

        """
        a = Artifact(*data)
        a._load()
        return a
