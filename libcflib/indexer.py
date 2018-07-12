"""
Index the artifacts.
"""

import bz2
import io
import os
import glob
from collections import defaultdict
from typing import Dict, Set

try:
    from pandas._lib.json import load as load_json_file
except ImportError:
    import json
    load_json_file = json.load

from concurrent.futures import as_completed, ThreadPoolExecutor
from whoosh.fields import FieldConfigurationError

import requests
import tqdm

from .harvester import harvest
from .tools import expand_file_and_mkdirs
from .schemas import SCHEMA
from .whoosh.utils import create_whoosh_schema, add


def all_artifacts(root):
    files = glob.glob(f"{root}/*/*/*/*.json")
    for f in files:
        yield f.replace(f"{root}/", "")


def indexed_artifacts(root):
    try:
        for res in search(index, {}):
            yield os.path.join(root, res["pkg"], res["channel"], res["arch"], res["name"] + '.json')
    except FieldConfigurationError:
        raise StopIteration


def unindexed_artifacts(root):
    artifacts = list(all_artifacts(root))
    indexed = list(indexed_artifacts(root))
    return set(artifacts) - set(indexed)


def index_package(root_path, ix, artifact, progress_callback=None):
    if progress_callback:
        progress_callback()
    with open(artifact, "r") as f:
        data = load_json_file(f)
    package, channel, arch, name = artifact.split(os.sep)
    name = os.splitext(name)[0]
    schema = create_whoosh_schema(SCHEMAS["artifact"]["schema"])
    add(
        ix,
        schema=schema,
        pkg=package,
        channel=channel,
        arch=arch,
        name=name,
        **data,
    )


def index(path):
    ix = os.path.abspath(os.path.join(path, os.pardir, "whoosh"))
    unindexed_artifacts = unindexed_artifacts(path, ix)
    print(f"TOTAL UNINDEXED ARTIFACTS: {len(sorted_files)}")
    unindexed_artifacts = unindexed_artifacts[:500]
    progress = tqdm.tqdm(total=len(sorted_files))
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [
            pool.submit(
                index_artifact,
                path,
                ix,
                artifact,
                progress_callback=progress.update,
            )
            for artifact in unindexed_artifacts
        ]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_path")
    args = parser.parse_args()
    print(args)
    index(args.root_path)
