import collections.abc
import hashlib
import json
import os
import time

try:
    from conda.models.version import VersionOrder
except ImportError:
    pass
import networkx as nx
import requests

from libcflib.chained_db import ChainDB, _convert_to_dict
from libcflib.tools import parse_meta_yaml, indir
from libcflib.logger import LOGGER



def get_attrs(yaml_dict):
    """Extract top level metadata (mostly used for the migration bot) from
    parsed `meta.yaml` from the artifact

    Parameters
    ----------
    yaml_dict : dict
        The parsed `meta.yaml` from the artifact `raw_recipe`

    Returns
    -------
    sub_graph : dict
        The node attributes
    """
    sub_graph = {}
    name = yaml_dict['package']['name']
    if not yaml_dict:
        LOGGER.warn('Something odd happened when parsing recipe '
                    '{}'.format(name))
        sub_graph['bad'] = 'Could not parse'
        return sub_graph
    req = set(yaml_dict.get('requirements', set()))
    if req:
        # TODO: pull requirements from all the renderings
        for sub in ['build', 'host', 'run']:
            req |= set([x.split()[0] for x in list(
                req.get(sub, []) if req.get(sub, []) is not None else [])])
    sub_graph['req'] = req

    keys = [('package', 'name'), ('package', 'version')]
    missing_keys = [k[1] for k in keys if k[1] not in
                    yaml_dict.get(k[0], {})]
    source = yaml_dict.get('source', [])
    if isinstance(source, collections.abc.Mapping):
        source = [source]
    source_keys = set()
    for s in source:
        if not sub_graph.get('url'):
            sub_graph['url'] = s.get('url')
        source_keys |= s.keys()
    if 'url' not in source_keys:
        missing_keys.append('url')
    if missing_keys:
        LOGGER.warn("Recipe {} doesn't have a {}".format(name,
                    ', '.join(missing_keys)))
        sub_graph['bad'] = missing_keys
    for k in keys:
        if k[1] not in missing_keys:
            sub_graph[k[1]] = yaml_dict[k[0]][k[1]]
    k = next(iter((source_keys & hashlib.algorithms_available)), None)
    if k:
        sub_graph['hash_type'] = k

    return sub_graph


def create_graphs():
    dir0 = $LIBCFGRAPH_DIR
    new_graphs = {}
    for package in os.listdir(os.path.join(dir0, 'artifacts')):
        dir1 = os.path.join(dir0, package)
        for channel in $LIBCFGRAPH_CHANNELS:
            with open(os.path.join(dir0, channel + '.json')) as f:
                graph = nx.node_link_graph(json.load(f))
            new_graphs[channel] = nx.DiGraph()
            dir2 = os.path.join(dir1, channel)
            attrs = ChainDB(graph.nodes[package])
            for arch in os.listdir(dir2):
                dir3 = os.path.join(dir2, arch)
                with indir(dir3):
                    latest_version = max(map(VersionOrder, g`*.json`[-1]))
                    with open(latest_version + '.json', 'r') as f:
                        art = json.load(f)
                        parsed_recipe = parse_meta_yaml(art['raw_recipe'])
                        sub_attrs = get_attrs(parsed_recipe)
                        edge_kwags = dict(arch=arch, channel=channel)
                        for dep in sub_attrs.get('req', []):
                            if graph.has_edge(dep, package):
                                graph.edges[(dep, package)].update(edge_kwags)
                            else:
                                graph.add_edge(dep, package, **edge_kwags)
                        attrs.maps.append(sub_attrs)
            new_graphs[channel].add_node(package, **_convert_to_dict(attrs))
    return new_graphs


def update_graphs():
    for k, v in create_graphs():
        with open(k+'.json', 'w') as f:
            json.dump(nx.node_link_data(v), f)
