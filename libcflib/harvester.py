"""
Harvests metadata out of a built conda package
"""

import tarfile
import os
import json
import io
import sys

import ruamel_yaml


def filter_file(filename):
    if not filename:
        return False
    fn, ext = os.path.splitext(filename)
    if ext in {'.txt', '.pyc'}:
        return False
    else:
        return True


def harvest(io_like):
    tf = tarfile.open(fileobj=io_like, mode='r:bz2')

    # info/files
    file_listing = tf.extractfile('info/files').readlines()
    file_listing = (fn.decode('utf8').strip() for fn in file_listing if fn)
    file_listing = [filter_file(fn) for fn in file_listing]

    # info/recipe/meta.yaml
    rendered_recipe = ruamel_yaml.safe_load(tf.extractfile('info/recipe/meta.yaml'))
    raw_recipe = tf.extractfile('info/recipe/meta.yaml.template').read().decode('utf8')
    conda_build_config = ruamel_yaml.safe_load(
        tf.extractfile('info/recipe/conda_build_config.yaml'))
    about = json.load(tf.extractfile('info/about.json'))
    index = json.loads(tf.extractfile('info/index.json'))

    return {
        'name': index['name'],
        'version': index['version'],
        'index': index,
        'about': about,
        'rendered_recipe': rendered_recipe,
        'raw_recipe': raw_recipe,
        'conda_build_config': conda_build_config,
        'files': file_listing
    }


def harvest_from_filename(filename):
    with open(filename, 'rb') as fo:
        return harvest(fo)


if __name__ == '__main__':
    o = harvest_from_filename(sys.argv[1])
    output = io.StringIO()
    ruamel_yaml.dump(o, output)
    print(output.getvalue())
