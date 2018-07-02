"""Module for representing entities of the graph"""
import builtins
from collections import defaultdict
import os
from typing import Iterator

from lazyasd import lazyobject

try:
    from pandas._lib.json import load as load_json_file
except ImportError:
    import json
    load_json_file = json.load

from libcflib.tools import indir


@lazyobject
def DB():
    """Lazily loaded database object."""
    from libcflib import db
    return db.DB()


class Model(object):
    def __init__(self):
        self._d = {}
        self._loaded = False

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
        self._loaded = True

    def asdict(self,):
        """Returns the dictionary view of the artifact"""
        if not self._loaded:
            self._load()
        return self._d


class Artifact(Model):
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

    def _load(self):
        env = builtins.__xonsh_env__
        filename = os.path.join(env.get("LIBCFGRAPH_DIR"), "artifacts", self._path)
        with open(filename, "r") as f:
            self._d.update(load_json_file(f))
        super()._load()


class ChannelGraph(Model):
    """Lazily loaded channel graph model"""

    def __init__(self, name):
        """
        Parameters
        ----------
        name : str
            The name of the channel graph to load.
        """
        super().__init__()
        self.name = self._name = name

    def __repr__(self):
        return f"ChannelGraph({self.name!r})"

    def _load(self):
        env = builtins.__xonsh_env__
        filename = os.path.join(env.get("LIBCFGRAPH_DIR"), self._name + ".json")
        # TODO: use networkx to get the data so we have edges
        with open(filename, "r") as f:
            self._d.update(load_json_file(f))
        super()._load()


class Package(Model):
    """Lazily loaded package model"""

    def __init__(self, *, name=None):
        super().__init__()
        self.name = self._name = name

    def __repr__(self):
        return f"Package({self.name!r})"

    def _load(self):
        env = builtins.__xonsh_env__
        arches = set()
        channels = set()
        artifacts = defaultdict(lambda: defaultdict(set))
        for channel, graph in DB.channel_graphs.items():
            pkg = graph.get(self._name, None)
            if pkg is None:
                # package does not exist on this channel
                continue
            # FIXME: This probably needs to do a deep merge, rather than update
            self._d.update(pkg)
            channels.add(channel)
            channel_dir = os.path.join($LIBCFGRAPH_DIR, 'artifacts', self._name, channel)
            with indir(channel_dir):
                arch_names = g`*`
            arches.update(arch_names)
            for arch in arch_names:
                arch_dir = os.path.join(channel_dir, arch)
                with indir(arch_dir):
                    artifacts[channel][arch].update(g`*.json`)
        self.arches = arches
        self.channels = channels
        self.artifacts = artifacts
        super()._load()


class Feedstock(Model):
    def __init__(self, *, name=None):
        self._name = name
        super().__init__()

    def _load(self):
        env = builtins.__xonsh_env__
        filename = os.path.join(
            env.get("LIBCFGRAPH_DIR"), "conda-forge-feedstocks.json"
        )
        with open(filename, "r") as f:
            self._d.update(load_json_file(f).get(self._name, {}))
        super()._load()
