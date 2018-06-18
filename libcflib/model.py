"""Module for representing entities of the graph"""
import json
import os
from collections.abc import MutableMapping
from typing import Iterator


class Artifact(MutableMapping):
    """Representation of an artifact via a lazy json load"""
    EXCLUDE_LOAD = ['loaded', 'name', 'folder']

    def __init__(self, *args):
        self.loaded = False
        self.args = args[:-1] + ((args[-1] + '.json'), )
        super().__init__()

    def __iter__(self) -> Iterator:
        self._load()
        return iter(self.__dict__)

    def __len__(self) -> int:
        self._load()
        return len(self.__dict__)

    def __getitem__(self, k):
        if k not in self.EXCLUDE_LOAD:
            self._load()
        return self.__dict__[k]

    def __delitem__(self, k) -> None:
        if k not in self.EXCLUDE_LOAD:
            self._load()
        del self.__dict__[k]

    def __setitem__(self, k, v) -> None:
        if k not in self.EXCLUDE_LOAD:
            self._load()
        self.__dict__[k] = v

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    # TODO: make this into a decorator
    def _load(self):
        if not self.loaded:
            with open(os.path.join(*self.args), 'r') as f:
                self.loaded = True
                self.update(json.load(f))

