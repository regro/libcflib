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


def _all_artifacts(root):
    files = glob.glob(f"{root}/*/*/*/*.json")
    for f in files:
        yield f.replace(f"{root}/", "")


def _indexed_artifacts(root, ix):
    with ix.searcher() as searcher:
        for fields in searcher.all_stored_fields():
            yield fields["path"]


def _unindexed_artifacts(root, ix):
    artifacts = set(_all_artifacts(root))
    indexed = set(_indexed_artifacts(root, ix))
    return artifacts - indexed


def get_artifact(root_path, artifact, progress_callback=None):
    """Get the data from an artifact file.

    Parameters
    ----------
    root_path : str
        A path to the directory containing the artifact.
    artifact : str
        The path to the artifact relative to `root_path`.

    Returns
    -------
    dict
        The data from the artifact file.
    """

    if progress_callback:
        progress_callback()
    with open(os.path.join(root_path, artifact), "r") as f:
        data = load_json_file(f)
    package, channel, arch, name = artifact.split(os.sep)
    name = os.path.splitext(name)[0]
    data.update(
        {
            "path": artifact,
            "pkg": package,
            "channel": channel,
            "arch": arch,
            "filename": name,
        }
    )
    return data


def index(path):
    """Index all of the artifacts in a specified directory.

    Parameters
    ----------
    path : str
        The path to the directory containing the artifacts to be indexed.
    """
    raise NotImplementedError("indexer needs to be rewritten to not use whoosh")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_path")
    args = parser.parse_args()
    print(args)
    index(args.root_path)
