"""Module for representing entities of the graph"""
import os
import json
from typing import Iterator
from collections.abc import MutableMapping


class Artifact(MutableMapping):
    """Representation of an artifact via a lazy json load.
    Either the filename path or the pkg, channel, arch, and name
    must be given.
    """
    EXCLUDE_LOAD = frozenset(['loaded', 'args'])

    def __init__(self, *, pkg=None, channel=None, arch=None, name=None,
                 path=None):
        """
        Parameters
        ----------
        pkg : str or None, optional
            Package name
        channel : str or None, optional
            Channel name
        arch : str or None, optional
            Architeture name
        name : str or None, optional
            Fully resolved name, without *.tar.bz2 or *.json
        path : str or None, optional
            Path to artifact file. This is relative to the libcfgraph repo dir.
        """
        self.loaded = False
        if path is not None:
            self.path = path
        elif (pkg is not None and channel is not None and
              arch is not None and name is not None):
            if name.endswith('.tar.bz2'):
                name = name[:-8]
            self.path = os.path.join(pkg, channel, arch, name + '.json')
        else:
            msg = 'Artifact path or pkg, channel, arch and name must be given. '
            msg += f'Got path={path!r}, pkg={pkg!r}, channel={channel!r}, '
            msg += f'arch={arch!r}, name={name!r}.'
            raise ValueError(msg)
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

    def _load(self):
        if not self.loaded:
            env = builtins.__xonsh_env__
            filename = os.path.join(env.get('LIBCFGRAPH_DIR'), self.path)
            with open(filename, 'r') as f:
                self.loaded = True
                self.update(json.load(f))
