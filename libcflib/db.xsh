"""Database for accessing graph information"""
import os

import zict

from .model import Artifact

class DB:
    """A logging object for fixie that stores information in line-oriented JSON
    format.
    """

    __inst = None

    def __new__(cls):
        # make the logger a singleton
        if DB.__inst is None:
            DB.__inst = object.__new__(cls)
        return DB.__inst

    def __init__(self, history=100):
        """

        Parameters
        ----------
        history: int
            Size of the cache

        Caching forked from Streamz
        Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        All rights reserved.

        """
        if os.path.exists($LIBCFGRAPH_DIR):
            git pull $LIBCFGRAPH_URL master
        else:
            git clone $LIBCFGRAPH_URL $LIBCFGRAPH_DIR
        self.cache_dict = {}
        self.cache = zict.LRU(history, self.cache_dict)

    def _build_whoosh(self):
        self.whoosh = 'whoosh'


    def search(self, **kwargs):
        """Search the database

        Parameters
        ----------
        kwargs: dict
            The keys to search on

        Yields
        -------
        res:
            The loaded artifact search results

        Caching forked from Streamz
        Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        All rights reserved.
        """
        # INSERT WHOOSH HERE
        results = (i for i in range(10))
        for result in results:
            data = self.get_data(result)
            self.cache_dict[result] = data
            yield data

    def get_data(self, keys):
        """Get the artifact data from the database

        Parameters
        ----------
        keys

        Returns
        -------

        """
        a = Artifact(*keys)
        a._load()
        return a
