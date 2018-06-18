import json
import os

from collections.abc import MutableMapping
from typing import Iterator


class Node(MutableMapping):
    EXCLUDE_LOAD = ['loaded', 'name', 'folder']

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

    def __init__(self, name, folder):
        self.loaded = False
        self.name = name
        self.folder = folder
        super().__init__()

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    # TODO: make this into a decorator
    def _load(self):
        if not self.loaded:
            with open(os.path.join(self.folder, self.name+'.json'), 'r') as f:
                self.loaded = True
                self.update(json.load(f))

