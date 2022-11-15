"""
Harvests metadata out of a built conda package
"""

import io
import json
import os
import sys
import tarfile

from ruamel_yaml.scanner import ScannerError
import ruamel_yaml

METADATA_VERSION = 1


def filter_file(filename):
    if not filename:
        return False
    fn, ext = os.path.splitext(filename)
    if ext in {".txt", ".pyc"}:
        return False
    else:
        return True


# There are some meta.yaml files that were written weirdly and have some strange tag
# information in them.  This is not parsable by safe loader, so we add some more
# fallback loading
def yaml_construct_fallback(loader, node):
    return None


ruamel_yaml.add_constructor(
    "tag:yaml.org,2002:python/object/apply:builtins.getattr",
    yaml_construct_fallback,
    constructor=ruamel_yaml.SafeConstructor,
)
ruamel_yaml.add_constructor(
    "tag:yaml.org,2002:python/object:__builtin__.instancemethod",
    yaml_construct_fallback,
    constructor=ruamel_yaml.SafeConstructor,
)


def harvest_dot_conda(io_like, filename):
    from conda_package_streaming import package_streaming
    stream = package_streaming.stream_conda_component(
        filename, io_like, component=package_streaming.CondaComponent.info
    )
    data = harvest_tarfile(stream)
    stream.close()

    return data


def harvest(io_like):
    tf = tarfile.open(fileobj=io_like, mode="r:bz2")
    return harvest_tarfile(tf)


def harvest_tarfile(tf_or_stream):
    rendered_recipe = {}
    index = {}
    about = {}
    raw_recipe = ""
    conda_build_config = {}
    raw_recipe_backup = ""

    for _data in tf_or_stream:
        if isinstance(_data, tarfile.TarInfo):
            mem = _data
            tf = tf_or_stream
        else:
            tf, mem = _data

        if mem.name == "info/files":
            # info/files
            file_listing = tf.extractfile(mem).readlines()
            file_listing = [fn.decode("utf8").strip() for fn in file_listing if fn]
            file_listing = [fn for fn in file_listing if filter_file(fn)]
        elif mem.name == "info/recipe/meta.yaml":
            raw_recipe_backup = tf.extractfile(mem).read(mem.size).decode("utf8")
            # info/recipe/meta.yaml
            try:
                rendered_recipe = ruamel_yaml.safe_load(raw_recipe_backup)
            except ScannerError:
                # Non parseable
                rendered_recipe = {}
        elif mem.name == "info/meta.yaml":
            # older artifacts have a meta.yaml in another location
            try:
                rendered_recipe = ruamel_yaml.safe_load(tf.extractfile(mem).read(mem.size))
            except ScannerError:
                # Non parseable
                rendered_recipe = {}
        elif mem.name == "info/about.json":
            about = json.loads(tf.extractfile(mem).read(mem.size))
        elif mem.name == "info/index.json":
            index = json.loads(tf.extractfile(mem).read(mem.size))
        elif mem.name == "info/recipe/meta.yaml.template":
            raw_recipe = tf.extractfile(mem).read(mem.size).decode("utf8")
        elif mem.name == "info/recipe/conda_build_config.yaml":
            conda_build_config = ruamel_yaml.safe_load(tf.extractfile(mem).read(mem.size))

    return {
        "metadata_version": METADATA_VERSION,
        "name": index.get("name", ""),
        "version": index.get("version", ""),
        "index": index,
        "about": about,
        "rendered_recipe": rendered_recipe,
        "raw_recipe": raw_recipe if len(raw_recipe) > 0 else raw_recipe_backup,
        "conda_build_config": conda_build_config,
        "files": file_listing,
    }


def harvest_from_filename(filename):
    with open(filename, "rb") as fo:
        if filename.endswith(".tar.bz2"):
            return harvest(fo)
        elif filename.endswith(".conda"):
            return harvest_dot_conda(fo, filename)
        else:
            raise RuntimeError(f"File '{filename}' is not a recognized conda format!")


if __name__ == "__main__":
    o = harvest_from_filename(sys.argv[1])
    output = io.StringIO()
    ruamel_yaml.dump(o, output)
    print(output.getvalue())
