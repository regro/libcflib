"""Module for representing entities of the graph"""
import os
import re
import builtins
from collections import defaultdict
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

    def __eq__(self, other):
        if not self._loaded:
            self._load()
        if isinstance(other, Model) and not other._loaded:
            other._load()
        return self._d == other._d

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
            if hasattr(self._d, name):
                return getattr(self._d, name)
            elif name in self._d:
                return self._d[name]
            else:
                raise AttributeError(f"{self} does not have attribute {name!r}")

    def __setattr__(self, name, value):
        if name.startswith("_") or name in self.__dict__:
            self.__dict__[name] = value
        elif hasattr(self._d, name):
            setattr(self._d, name, value)
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

    def __repr__(self):
        return f"Artifact(path={self._path!r})"

    def _load(self):
        env = builtins.__xonsh__.env
        filename = os.path.join(env.get("LIBCFGRAPH_DIR"), "artifacts", self._path)
        with open(filename, "r") as f:
            self._d.update(load_json_file(f))
        super()._load()


@lazyobject
def int_re():
    return re.compile(r'(\d+)')


def safe_int(s, default=0):
    """convert a vresion number to an int, safely"""
    m = int_re.search(s)
    if m is None:
        n = default
    else:
        n = int(m.group(1))
    return n


def artifact_key(artifact):
    """A function for sorting artifacts"""
    major, _, remain = artifact.version.partition('.')
    minor, _, micro = remain.partition('.')
    major = safe_int(major)
    minor = safe_int(minor)
    micro = safe_int(micro)
    return (major, minor, micro, artifact.index['build_number'],
            artifact.index['build'], artifact._path)


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
        env = builtins.__xonsh__.env
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
        env = builtins.__xonsh__.env
        arches = set()
        channels = set()
        artifacts = defaultdict(lambda: defaultdict(set))
        for channel, graph in DB.channel_graphs.items():
            # the following does not actually work, since graph is always empty
            #pkg = graph.get(self._name, None)
            #if pkg is None:
                # package does not exist on this channel
            #    continue
            # FIXME: This probably needs to do a deep merge, rather than update
            #self._d.update(pkg)
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

    def latest_artifact(self, channels=('conda-forge',),
                        arches=('linux-64', 'osx-64', 'win-64'),
                        include_noarch=True):
        """Finds the latest artifact, given channel and arch preferences.
        noarch is included with any arch packages by default.
        """
        # find channel
        channel = None
        for c in channels:
            if c in self.channels:
                channel = c
                break
        else:
            raise ValueError(f"channels {channels} not available for {self.name}")
        # find arch
        arch = None
        for a in arches:
            if a in self.arches:
                arch = a
                break
        else:
            if not include_noarch or 'noarch' not in self.arches:
                raise ValueError(f"arches {arches} not available for {self.name}")
        # add arch artifacts
        artifacts = set()
        if arch is not None:
            for art in self.artifacts[channel][arch]:
                path = os.path.join(self.name, channel, arch, art)
                artifacts.add(DB.get_artifact(path=path))
        if include_noarch and 'noarch' in self.arches:
            for art in self.artifacts[channel]['noarch']:
                path = os.path.join(self.name, channel, 'noarch', art)
                artifacts.add(DB.get_artifact(path=path))
        # sort and return latest
        artifacts = sorted(artifacts, key=artifact_key, reverse=True)
        return artifacts[0]


class Feedstock(Model):
    def __init__(self, *, name=None):
        self._name = name
        super().__init__()

    def _load(self):
        env = builtins.__xonsh__.env
        filename = os.path.join(
            env.get("LIBCFGRAPH_DIR"), "conda-forge-feedstocks.json"
        )
        with open(filename, "r") as f:
            self._d.update(load_json_file(f).get(self._name, {}))
        super()._load()
