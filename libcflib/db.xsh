"""Database for accessing graph information"""
import os
import time

import toolz
import zict

from libcflib.tools import indir
from libcflib.logger import LOGGER
from libcflib.models import Artifact, Package, ChannelGraph


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
        """
        # Caching forked from Streamz
        # Copyright (c) 2017, Continuum Analytics, Inc. and contributors
        # All rights reserved.
        if self._initialized:
            return
        if os.path.exists($LIBCFGRAPH_DIR):
            LOGGER.log('pulling latest graph', category="db")
            with indir($LIBCFGRAPH_DIR):
                git pull $LIBCFGRAPH_URL master -s recursive -X theirs --no-edit
        else:
            LOGGER.log('grabbing initial graph', category="db")
            git clone --quiet $LIBCFGRAPH_URL $LIBCFGRAPH_DIR
        self.cache = {}
        cache_size = $LIBCFLIB_DB_CACHE_SIZE if cache_size is None else cache_size
        self.lru = zict.LRU(cache_size, self.cache)
        self.times = {}
        self._channel_graphs = {}
        self._packages = {}
        self._initialized = True
        self._idx = $LIBCFGRAPH_INDEX

    def search(self, query, *, page_num=1, page_size=10):
        """Search the database

        Parameters
        ----------
        query : str
            The query string to search the artifacts for.
        page_num : int
            Which page number to return.
        page_size : int
            How many results per page

        Yields
        -------
        res : Artifact
            The loaded artifact search results
        """
        artifactsdir = $LIBCFGRAPH_DIR + '/artifacts/'
        n_artifactsdir = len(artifactsdir)
        grep_args = ['-r', '--files-with-matches', query, artifactsdir]
        for line in !(grep @(grep_args) | head -n @(page_num * page_size) | tail -n @(page_size)):
            path = line[n_artifactsdir:-1]
            artifact = self.get_artifact(path=path)
            yield artifact

    def load_channel_graphs(self):
        """Loads channel data for known channels"""
        with indir($LIBCFGRAPH_DIR):
            for fname in g`*.json`:
                name = fname[:-5]
                self._channel_graphs[name] = ChannelGraph(name)

    @property
    def channel_graphs(self):
        if not self._channel_graphs:
            self.load_channel_graphs()
        return self._channel_graphs

    def load_packages(self):
        """Loads package data for known package"""
        with indir($LIBCFGRAPH_DIR + '/artifacts/'):
            package_names = g`*`
        for name in package_names:
            self._packages[name] = Package(name=name)

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
