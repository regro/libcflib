"""
Index the artifacts.
"""

import os
import glob

try:
    from pandas._lib.json import load as load_json_file
except ImportError:
    import json

    load_json_file = json.load

from concurrent.futures import as_completed, ThreadPoolExecutor
from whoosh.fields import ID, TEXT

import tqdm

from .schemas import SCHEMAS
from .whoosh.utils import create_whoosh_schema, get_index


def all_artifacts(root):
    files = glob.glob(f"{root}/*/*/*/*.json")
    for f in files:
        yield f.replace(f"{root}/", "")


def indexed_artifacts(ix):
    with ix.searcher() as searcher:
        for fields in searcher.all_stored_fields():
            yield fields["path"]


def unindexed_artifacts(root, ix):
    artifacts = set(all_artifacts(root))
    indexed = set(indexed_artifacts(ix))
    return artifacts - indexed


def get_artifact(root_path, artifact, progress_callback=None):
    if progress_callback:
        progress_callback()
    with open(artifact, "r") as f:
        data = load_json_file(f)
    package, channel, arch, name = artifact.split(os.sep)
    name = os.splitext(name)[0]
    data.update(
        {
            "path": artifact,
            "pkg": package,
            "channel": channel,
            "arch": arch,
            "name": name,
        }
    )
    return data


def index(path):
    ind = os.path.abspath(os.path.join(path, os.pardir, "whoosh"))
    schema = create_whoosh_schema(SCHEMAS["artifact"]["schema"])
    schema.add("pkg", TEXT(stored=True))
    schema.add("channel", TEXT(stored=True))
    schema.add("arch", TEXT(stored=True))
    schema.add("name", TEXT(stored=True))
    schema.add("path", ID(stored=True, unique=True))
    ix = get_index(ind, schema=schema)

    unindexed = unindexed_artifacts(path, ix)
    print(f"TOTAL UNINDEXED ARTIFACTS: {len(unindexed)}")
    unindexed = unindexed_artifacts[:500]
    progress = tqdm.tqdm(total=len(unindexed))

    writer = ix.writer()
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [
            pool.submit(get_artifact, path, artifact, progress_callback=progress.update)
            for artifact in unindexed
        ]
        for f in as_completed(futures):
            try:
                data = f.result()
            except Exception:
                pass
            else:
                writer.add_document(**data)
    writer.commit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_path")
    args = parser.parse_args()
    print(args)
    index(args.root_path)
