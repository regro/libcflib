"""Update the top level graph"""
import json
import os

try:
    from conda.models.version import VersionOrder
except ImportError:
    pass
import networkx as nx

from libcflib.tools import indir


def create_graphs():
    dir0 = os.path.join($LIBCFGRAPH_DIR, 'artifacts')
    channel_graphs = {}
    with indir(dir0):
        for art_fp in g`**.json`:
            pkg, channel, arch, art_file = art_fp.split('/')[-4:]
            if channel not in channel_graphs:
                channel_graphs[channel] = nx.DiGraph()
            with open(art_fp, 'r') as f:
                art = json.load(f)
                req = set()
                for sec, deps in art['rendered_recipe']['requirements'].items():
                    for dep in deps:
                        req.add(dep.split(' ')[0])
            if pkg not in channel_graphs[channel]:
                channel_graphs[channel].add_node(pkg)
            for k in ['versions', 'archs', 'req']:
                if k not in channel_graphs[channel].nodes[pkg]:
                    channel_graphs[channel].nodes[pkg][k] = set()

            channel_graphs[channel].nodes[pkg]['archs'].add(arch)
            channel_graphs[channel].nodes[pkg]['versions'].add(art['version'])
            channel_graphs[channel].nodes[pkg]['req'].update(req)

            for dep in channel_graphs[channel].nodes[pkg]['req']:
                if (dep, pkg) not in channel_graphs[channel].edges:
                    channel_graphs[channel].add_edge(dep, pkg, arch=set())
                channel_graphs[channel].edges[(dep, pkg)]['arch'].add(arch)
    return channel_graphs


def update_graphs():
    for k, v in create_graphs():
        with open(k+'.json', 'w') as f:
            json.dump(nx.node_link_data(v), f)
