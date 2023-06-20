import sys
import glob
import hashlib
import json
import os
from collections import defaultdict
from json import JSONDecodeError
from pathlib import Path
from typing import List

from tqdm import tqdm

from libcflib.jsonutils import dump, load
from concurrent.futures import as_completed, ThreadPoolExecutor
from itertools import groupby, chain

CLOBBER_EXCEPTIONS = {
    "matplotlib",
    "matplotlib-base",
    "mongo",
}

NUM_LETTERS = 5

IMPORT_TO_PKG_DIR = "import_to_pkg_maps"
IMPORT_TO_PKG_DIR_INDEX = f".{IMPORT_TO_PKG_DIR}_indexed_files"
IMPORT_TO_PKG_DIR_CLOBBERING = f"{IMPORT_TO_PKG_DIR}_clobbering_pkgs.json"
IMPORT_TO_PKG_DIR_META = f"{IMPORT_TO_PKG_DIR}_meta.json"
IMPORT_TO_PKG_DIR_SHARD = 10


def _get_head_letters(name):
    return name[:min(NUM_LETTERS, len(name))].lower()


def _fname_to_index(fname):
    return (
        abs(int(hashlib.sha1(fname.encode("utf-8")).hexdigest(), 16))
        % IMPORT_TO_PKG_DIR_SHARD
    )


def file_path_to_import(file_path: str):
    file_path = file_path.split("site-packages/")[-1].split(".egg/")[-1]
    if ".so" in file_path:
        if "python" not in file_path and "pypy" not in file_path:
            return
        file_path = file_path.split(".", 1)[0]
    elif ".pyd" in file_path:
        file_path = file_path.split(".", 1)[0]
    return (
        file_path.replace("/__init__.py", "")
        .replace("/__main__.py", "")
        .replace(".py", "")
        .replace(".pyd", "")
        .replace("/", ".")
    )


def extract_importable_files(file_list):
    output_list = []
    for file in file_list:
        if "site-packages/" in file:
            if file.rsplit("/", 1)[0] + "/__init__.py" in file_list:
                output_list.append(file)
            elif file.endswith(".so") or file.endswith(".pyd"):
                output_list.append(file)
            elif (
                len(file.split("site-packages/")[-1].split(".egg/")[-1].split("/")) == 1
            ):
                output_list.append(file)
    return output_list


def get_imports_and_files(file):
    with open(file) as f:
        data = json.load(f)

    pkg_files: List[str] = extract_importable_files(data.get("files", []))
    # TODO: handle top level things that are stand alone .py files
    return (
        {
            file_path_to_import(pkg_file)
            for pkg_file in pkg_files
            if any(pkg_file.endswith(k) for k in [".py", ".pyd", ".so"])
        }
        - {None},
        data.get("files", []),
    )


def write_sharded_dict(import_map):
    for k, v in groupby(import_map, lambda x: _get_head_letters(x)):
        with open(f"{IMPORT_TO_PKG_DIR}/{k}.json", "w") as f:
            dump({sk: import_map[sk] for sk in v}, f)


def read_sharded_dict():
    d = {}
    for file in os.listdir(IMPORT_TO_PKG_DIR):
        with open(file) as f:
            d.update(load(f))
    return d


def write_out_maps(gn, import_map):
    try:
        with open(f"{IMPORT_TO_PKG_DIR}/{gn}.json", "r") as f:
            old_map = load(f)
    except (FileNotFoundError, JSONDecodeError):
        old_map = import_map
    else:
        for k in list(import_map):
            old_map.setdefault(k, set()).update(import_map.pop(k))
    with open(f"{IMPORT_TO_PKG_DIR}/{gn}.json", "w") as f:
        dump(old_map, f)


if __name__ == "__main__":
    import_map = defaultdict(set)
    try:
        with open(IMPORT_TO_PKG_DIR_INDEX, "r") as f:
            indexed_files = {ff.strip() for ff in f.readlines()}
    except FileNotFoundError:
        # sharded variant
        indexed_files = set()
        try:
            for i in range(IMPORT_TO_PKG_DIR_SHARD):
                with open(f"{IMPORT_TO_PKG_DIR}_{i}", "r") as f:
                    indexed_files.update({ff.strip() for ff in f.readlines()})
        except FileNotFoundError:
            indexed_files = set()

    clobbers = set()

    if len(sys.argv) > 1:
        n_max = int(sys.argv[1])
    else:
        n_max = 10_000

    futures = {}
    all_files = set(glob.glob("artifacts/**/*.json", recursive=True))
    new_files = all_files - indexed_files

    with ThreadPoolExecutor(max_workers=4) as tpe:
        n_sub = 0
        for file in tqdm(
            new_files, total=min(n_max, len(new_files)), desc="submitting jobs"
        ):
            if os.path.exists(file) and os.path.isfile(file):
                artifact_name = Path(file).name.rsplit(".", 1)[0]
                futures[tpe.submit(get_imports_and_files, file)] = (artifact_name, file)
                n_sub += 1

            if n_sub == n_max:
                break

        del new_files

        files_indexed = set()
        for future in tqdm(as_completed(futures), total=len(futures), desc="getting results"):
            f, fext = futures.pop(future)
            files_indexed.add(fext)
            imports, files = future.result()
            pkg = f.rsplit("-", 2)[0]
            for impt in imports:
                import_map[impt].add(pkg)
                if (
                    not impt.startswith(pkg.replace("-", "_"))
                    and pkg not in CLOBBER_EXCEPTIONS
                ):
                    clobbers.add(pkg)

        os.makedirs(IMPORT_TO_PKG_DIR, exist_ok=True)
        sorted_imports = sorted(import_map.keys(), key=lambda x: x.lower())
        for gn, keys in tqdm(groupby(sorted_imports, lambda x: _get_head_letters(x))):
            sub_import_map = {k: import_map.pop(k) for k in keys}
            tpe.submit(write_out_maps, gn, sub_import_map)

    fnames_by_index = {}
    for fname in chain(indexed_files, files_indexed):
        index = _fname_to_index(fname)
        fnames_by_index.setdefault(index, set()).add(fname)

    for index, fnames in fnames_by_index.items():
        with open(f"{IMPORT_TO_PKG_DIR_INDEX}_{index}", "w") as fp:
            fp.write("\n".join(sorted(fnames)))

    with open(IMPORT_TO_PKG_DIR_INDEX, "a") as f:
        for file in files_indexed:
            f.write(f"{file}\n")
    try:
        with open(IMPORT_TO_PKG_DIR_CLOBBERING, "r") as f:
            _clobbers = load(f)
    except FileNotFoundError:
        _clobbers = set()
    _clobbers.update(clobbers)

    with open(IMPORT_TO_PKG_DIR_CLOBBERING, "w") as f:
        dump(_clobbers, f)

    with open(IMPORT_TO_PKG_DIR_META, "w") as f:
        dump({"num_letters": NUM_LETTERS, "n_files": IMPORT_TO_PKG_DIR_SHARD}, f)
