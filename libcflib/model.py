"""Module for representing entities of the graph"""
import os
import json
import builtins
from typing import Iterator
from collections import defaultdict
from collections.abc import MutableMapping

import networkx as nx


class Package(MutableMapping):
    def __init__(self, *, name=None, artifact_ids=None, channel="conda-forge"):
        self.name = name
        self._path = channel + ".json"
        self._d = {}
        self._load()
        self.artifacts = defaultdict(lambda: defaultdict(set))
        for a in artifact_ids:
            _, channel, arch, artifact_name = a.split("/", 3)
            self.artifacts[channel][arch].add(artifact_name)

    def __iter__(self) -> Iterator:
        if not self._loaded:
            self._load()
        yield from self._d

    def __len__(self) -> int:
        if not self._loaded:
            self._load()
        return len(self._d)

    def __getitem__(self, key):
        if not self._loaded:
            self._load()
        return self._d[key]

    def __setitem__(self, key, value) -> None:
        if not self._loaded:
            self._load()
        self._d[key] = value

    def __delitem__(self, key) -> None:
        if not self._loaded:
            self._load()
        del self._d[key]

    def __getattr__(self, name):
        if name.startswith("_") or name in self.__dict__:
            return self.__dict__[name]
        else:
            if not self._loaded:
                self._load()
            return self._d[name]

    def __setattr__(self, name, value):
        if name.startswith("_") or name in self.__dict__:
            self.__dict__[name] = value
        else:
            self._d[name] = value

    def __hash__(self):
        return hash(self._path)

    def __repr__(self):
        return f"Package({self.name}"

    def _load(self):
        env = builtins.__xonsh_env__
        filename = os.path.join(env.get("LIBCFGRAPH_DIR"), self._path)
        with open(filename, "r") as f:
            self._d.update(nx.node_link_graph(json.load(f))[self.name])
        self._loaded = True

    def asdict(self,):
        """Returns the dictionary view of the package"""
        return self._d


class Artifact(MutableMapping):
    """Representation of an artifact via a lazy json load.
    Either the filename path or the pkg, channel, arch, and name
    must be given.
    """

    def __init__(self, *, pkg=None, channel=None, arch=None, name=None, path=None):
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
        self._d = {}
        self._loaded = False
        if path is not None:
            self._path = path
        elif (
            pkg is not None
            and channel is not None
            and arch is not None
            and name is not None
        ):
            if name.endswith(".tar.bz2"):
                name = name[:-8]
            self._path = os.path.join(pkg, channel, arch, name + ".json")
        else:
            msg = "Artifact path or pkg, channel, arch and name must be given. "
            msg += f"Got path={path!r}, pkg={pkg!r}, channel={channel!r}, "
            msg += f"arch={arch!r}, name={name!r}."
            raise ValueError(msg)
        super().__init__()

    def __iter__(self) -> Iterator:
        if not self._loaded:
            self._load()
        yield from self._d

    def __len__(self) -> int:
        if not self._loaded:
            self._load()
        return len(self._d)

    def __getitem__(self, key):
        if not self._loaded:
            self._load()
        return self._d[key]

    def __setitem__(self, key, value) -> None:
        if not self._loaded:
            self._load()
        self._d[key] = value

    def __delitem__(self, key) -> None:
        if not self._loaded:
            self._load()
        del self._d[key]

    def __getattr__(self, name):
        if name.startswith("_") or name in self.__dict__:
            return self.__dict__[name]
        else:
            if not self._loaded:
                self._load()
            return self._d[name]

    def __setattr__(self, name, value):
        if name.startswith("_") or name in self.__dict__:
            self.__dict__[name] = value
        else:
            self._d[name] = value

    def __hash__(self):
        return hash(self._path)

    def _load(self):
        env = builtins.__xonsh_env__
        filename = os.path.join(env.get("LIBCFGRAPH_DIR"), 'artifacts', self._path)
        with open(filename, "r") as f:
            self._d.update(json.load(f))
        self._loaded = True

    def asdict(self,):
        """Returns the dictionary view of the artifact"""
        if not self._loaded:
            self._load()
        return self._d
