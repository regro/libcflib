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

CLOBBER_EXCEPTIONS = {
    'matplotlib',
    'matplotlib-base',
    'mongo',
}


def file_path_to_import(file_path: str):
    file_path = file_path.split("site-packages/")[-1].split(".egg/")[-1]
    if '.so' in file_path:
        if 'python' not in file_path and 'pypy' not in file_path:
            return
        file_path = file_path.split('.', 1)[0]
    elif '.pyd' in file_path:
        file_path = file_path.split('.', 1)[0]
    return (
        file_path.replace("/__init__.py", "")
        .replace("/__main__.py", "")
        .replace(".py", "")
        .replace('.pyd', '')
        .replace("/", ".")
    )


def extract_importable_files(file_list):
    output_list = []
    for file in file_list:
        if 'site-packages/' in file:
            if file.rsplit('/', 1)[0]+"/__init__.py" in file_list:
                output_list.append(file)
    return output_list


def get_imports_and_files(file):
    with open(file) as f:
        data = json.load(f)

    pkg_files: List[str] = extract_importable_files(data.get("files", []))
    # TODO: handle top level things that are stand alone .py files
    return {
        file_path_to_import(pkg_file)
        for pkg_file in pkg_files
        if any(pkg_file.endswith(k) for k in ['.py', '.pyd', '.so'])
    } - {None}, data.get("files", [])


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

    clobbers = set()
    clobber_maps = defaultdict(lambda: defaultdict(set))

    futures = {}
    tpe = ThreadPoolExecutor()
    all_files = set(glob.glob("artifacts/**/*.json", recursive=True))
    new_files = all_files - indexed_files
    for file in new_files:
        futures[tpe.submit(get_imports_and_files, file)] = file
    for future in tqdm(as_completed(futures), total=len(futures)):
        file = futures.pop(future)

        artifact_name = Path(file).name.rsplit(".", 1)[0]
        parts = file.split("/")
        pkg = parts[1]
        platform = parts[3]

        imports, files = future.result()
        for impt in imports:
            pkg_name = futures[future].rsplit('-', 2)[0]
            if all(not impt.startswith(name) for name in [pkg_name, pkg_name.replace('-', '_')]) and pkg_name not in CLOBBER_EXCEPTIONS:
                clobbers.add(futures[future])
            import_map[impt].add(f)

        if platform == "noarch":
            for f in files:
                clobber_maps[platform][f].add(pkg)
                for _platform in ["linux-64", "osx-64", "win-64", "linux-aarch64", "linux-ppc64le", "osx-arm64"]:
                    clobber_maps[_platform][f].add(pkg)
        else:
            for f in files:
                clobber_maps[platform][f].add(pkg)

    os.makedirs("import_maps", exist_ok=True)
    sorted_imports = sorted(import_map.keys(), key=lambda x: x.lower())
    with tpe as pool:
        for gn, keys in tqdm(groupby(sorted_imports, lambda x: x[:2].lower())):
            sub_import_map = {k: import_map.pop(k) for k in keys}
            pool.submit(write_out_maps, gn, sub_import_map)

    with open(".indexed_files", "a") as f:
        for file in new_files:
            f.write(f"{file}\n")

    try:
        with open('clobbering_pkgs.json', 'r') as f:
            _clobbers = load(f)
    except FileNotFoundError:
        _clobbers = set()
    _clobbers.update(clobbers)

    with open('clobbering_pkgs.json', 'w') as f:
        dump(_clobbers, f)

    try:
        with open('file_map.json', 'r') as f:
            _clobber_maps: dict = load(f)
    except FileNotFoundError:
        _clobber_maps = dict()
    for platform, values in clobber_maps.items():
        z = _clobber_maps.setdefault(platform, {})
        for filename, pkgs in values.items():
            zz = z.setdefault(filename, set())
            zz.update(pkgs)
    with open('file_map.json', 'w') as f:
        dump(clobber_maps, f)
