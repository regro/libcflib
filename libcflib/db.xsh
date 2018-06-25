"""Database for accessing graph information"""
import os
import time

import toolz
import zict

from libcflib.tools import indir
from libcflib.logger import LOGGER
from libcflib.model import Artifact, Package


class DB:
    """A database interface to the graph information"""

    __inst = None

    def __new__(cls):
        # make the db a singleton
        if DB.__inst is None:
            DB.__inst = object.__new__(cls)
            DB.__inst._initialized = False
        return DB.__inst

    def __init__(self, cache_size=None):
        """

        Parameters
        ----------
        cache_size : int or None, optional
            Size of the cache, defaults to $LIBCFLIB_DB_CACHE_SIZE

        Caching forked from Streamz
        Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        All rights reserved.

        """
        if self._initialized:
            return
        if os.path.exists($LIBCFGRAPH_DIR):
            LOGGER.log('pulling latest graph', category="db")
            with indir($LIBCFGRAPH_DIR):
                git pull $LIBCFGRAPH_URL master
        else:
            LOGGER.log('grabbing initial graph', category="db")
            git clone $LIBCFGRAPH_URL $LIBCFGRAPH_DIR
        self.cache = {}
        cache_size = $LIBCFLIB_DB_CACHE_SIZE if cache_size is None else cache_size
        self.lru = zict.LRU(cache_size, self.cache)
        self.times = {}
        self._packages = {}
        self._initialized = True

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
                    data = self.get_artifact(**result)
                    self.cache[result] = data
                    # Cache the time so we can timeout the record
                    self.times[result] = time.time()
                else:
                    data = self.cache[results]
                yield data

    def load_packages(self):
        for package in os.listdir($LIBCFGRAPH_DIR + '/artifacts/'):
            p = Package(name=package)
            self._packages[p.name] = p

    @property
    def packages(self):
        """The packages dict."""
        if not self._packages:
            self.load_packages()
        return self._packages

    def get_artifact(self, **kwargs):
        """Get the artifact from the database.

        Parameters
        ----------
        kwargs :
            data for loading the artifact

        Returns
        -------
        The artifact
        """
        a = Artifact(**kwargs)
        a._load()
        return a
