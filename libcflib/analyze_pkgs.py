import glob
import json
from collections import defaultdict
from pathlib import Path
from typing import List

from tqdm import tqdm

from libcflib.jsonutils import dump, load
from concurrent.futures import as_completed, ThreadPoolExecutor


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


if __name__ == "__main__":
    import_map = defaultdict(set)
    try:
        with open("import_map.json") as f:
            import_map.update(load(f))
    except FileNotFoundError:
        pass

    try:
        with open(".indexed_files", "r") as f:
            indexed_files = f.readlines()
    except FileNotFoundError:
        indexed_files = []
    new_files = []
    futures = {}
    tpe = ThreadPoolExecutor()
    for file in tqdm(glob.glob("artifacts/**/*.json", recursive=True)):
        if file in indexed_files:
            continue
        else:
            new_files.append(file)
        artifact_name = Path(file).name.rsplit(".", 1)[0]
        futures[tpe.submit(get_imports, file)] = artifact_name
    for future in tqdm(as_completed(futures), total=len(futures)):
        for impt in future.result():
            import_map[impt].add(futures[future])
    with open("import_map.json", "w") as f:
        dump(import_map, f, indent=2)
    with open(".indexed_files", "a") as f:
        f.writelines(new_files)
