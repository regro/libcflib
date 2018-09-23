#!/usr/bin/env xonsh
import os
import json

from xonsh.tools import print_color

from binstar_client import errors
from binstar_client.utils import get_server_api, parse_specs

from libcflib.db import DB
import toolz


aserver_api = get_server_api()


def copy_label(spec, from_label, to_label):
    spec = parse_specs(spec)
    channels = aserver_api.list_channels(spec.user)
    label_text = 'label' if (from_label and to_label) else 'channel'

    from_label = from_label.lower()
    to_label = to_label.lower()

    if from_label not in channels:
        raise errors.UserError(
            "{} {} does not exist\n\tplease choose from: {}".format(
                label_text.title(),
                from_label,
                ', '.join(channels)
            ))

    if from_label == to_label:
        raise errors.UserError('--from-label and --to-label must be different: ' + spec)

    aserver_api.add_channel(
            to_label,
            spec.user,
            package=spec.package,
            version=spec._version,
            filename=spec._basename,
       )


db = DB()
all_noarch = g`$LIBCFGRAPH_DIR/artifacts/*/conda-forge/noarch/*`
prefix = $LIBCFGRAPH_DIR + '/artifacts/'
prefix_len = len(prefix)
all_noarch = [x[prefix_len:] for x in all_noarch]


def path_key(path):
    return path.partition('/')[0]


out = {}
for key, group in toolz.groupby(path_key, all_noarch).items():
    out[key] = group[-1]

if os.path.exists('relabeled.json'):
    with open('relabeled.json', 'r') as f:
        done = json.load(f)
else:
    done = {}

for name, artifact in out.items():
    if name in done:
        print_color('{GREEN}' + name + ' relabeled already{NO_COLOR}')
        continue
    pkg, channel, filename = artifact.split('/', 2)
    filename = os.path.splitext(filename)[0] + '.tar.bz2'
    _, version, _ = filename.rsplit('-', 2)
    spec = '/'.join([channel, pkg, version, filename])

    # copy
    print_color('Copying to gcc7 label: {YELLOW}' + spec + '{NO_COLOR}')
    copy_label(spec, 'main', 'gcc7')
    done[name] = artifact
    with open('relabled.json', 'w') as f:
        json.dump(done, f)

