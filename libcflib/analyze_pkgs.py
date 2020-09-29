import glob
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import List

from tqdm import tqdm

from libcflib.jsonutils import dump, load
from concurrent.futures import as_completed, ThreadPoolExecutor
from itertools import groupby


def file_path_to_import(file_path: str):
    return (
        file_path.replace("/__init__.py", "")
        .replace("/__main__.py", "")
        .replace(".py", "")
        .replace("/", ".")
    )


def get_imports(file):
    with open(file) as f:
        data = json.load(f)
    pkg_files: List[str] = [
        file.split("site-packages/")[-1].split(".egg/")[-1]
        for file in data.get("files", [])
        if "site-packages/" in file
    ]
    return {
        file_path_to_import(pkg_file)
        for pkg_file in pkg_files
        if pkg_file.endswith(".py")
    }


def write_sharded_dict(import_map):
    for k, v in groupby(import_map, lambda x: x[:2]):
        with open(f"import_maps/{k}.json", "w") as f:
            dump({sk: import_map[sk] for sk in v}, f)


def read_sharded_dict():
    d = {}
    for file in os.listdir("import_maps"):
        with open(file) as f:
            d.update(load(f))
    return d


def write_out_maps(gn, import_map):
    try:
        with open(f"import_maps/{gn}.json", "r") as f:
            old_map = load(f)
    except FileNotFoundError:
        old_map = import_map
    else:
        for k in list(import_map):
            old_map.setdefault(k, set()).update(import_map.pop(k))
    with open(f"import_maps/{gn}.json", "w") as f:
        dump(old_map, f, indent=2)


if __name__ == "__main__":
    import_map = defaultdict(set)
    try:
        with open(".indexed_files", "r") as f:
            indexed_files = {ff.strip() for ff in f.readlines()}
    except FileNotFoundError:
        indexed_files = set()
    futures = {}
    tpe = ThreadPoolExecutor()
    all_files = set(glob.glob("artifacts/**/*.json", recursive=True))
    new_files = all_files - indexed_files
    for file in new_files:
        artifact_name = Path(file).name.rsplit(".", 1)[0]
        futures[tpe.submit(get_imports, file)] = artifact_name
    for future in tqdm(as_completed(futures), total=len(futures)):
        f = futures.pop(future)
        for impt in future.result():
            import_map[impt].add(f)
    os.makedirs("import_maps", exist_ok=True)
    sorted_imports = sorted(import_map.keys(), key=lambda x: x.lower())
    with tpe as pool:
        for gn, keys in tqdm(groupby(sorted_imports, lambda x: x[:2].lower())):
            sub_import_map = {k: import_map.pop(k) for k in keys}
            pool.submit(write_out_maps, gn, sub_import_map)
    with open(".indexed_files", "a") as f:
        for file in new_files:
            f.write(f"{file}\n")
