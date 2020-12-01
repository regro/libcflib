import glob
import io
import json
import tarfile
from tempfile import TemporaryDirectory

import jedi

import os

import requests
from tqdm import tqdm

from libcflib.harvester import harvest
from libcflib.preloader import reap, ReapFailure
from libcflib.tools import expand_file_and_mkdirs


def file_path_to_import(file_path: str):
    return file_path.replace("/__init__.py", "").replace(".py", "").replace("/", ".")


def get_all_symbol_names(top_dir):
    # Note Jedi seems to pick up things that are protected by a
    # __name__ == '__main__' if statement
    # this could cause some over-reporting of viable imports this
    # shouldn't cause issues with an audit since we don't expect 3rd parties
    # to depend on those
    symbols_dict = {}
    module_import = top_dir.split("/")[-1]
    # walk all the files looking for python files
    for root, dirs, files in tqdm(os.walk(top_dir)):
        _files = [f for f in files if f.endswith(".py")]
        for file in _files:
            file_name = os.path.join(root, file)
            import_name = file_path_to_import(
                "".join(file_name.rpartition(module_import)[1:])
            )
            data = jedi.Script(path=file_name).complete()
            symbols_from_script = {
                k.full_name: k.type
                for k in data
                if k.full_name and module_import + "." in k.full_name
            }

            # cull statements within functions and classes, which are not importable
            classes_and_functions = {
                k for k, v in symbols_from_script.items() if v in ["class", "function"]
            }
            for k in list(symbols_from_script):
                for cf in classes_and_functions:
                    if k != cf and k.startswith(cf) and k in symbols_from_script:
                        symbols_from_script.pop(k)

            symbols_dict[import_name] = set(symbols_from_script)

    symbols = set()
    # handle star imports, which don't usually get added but are valid symbols
    for k, v in symbols_dict.items():
        symbols.update(v)
        symbols.update({f"{k}.{vv.rsplit('.', 1)[-1]}" for vv in v})
    return symbols


def harvest_imports(io_like):
    tf = tarfile.open(fileobj=io_like, mode="r:bz2")
    with TemporaryDirectory() as f:
        tf.extractall(path=f)
        return list(get_all_symbol_names(os.path.join(f, 'site-packages')))


def reap_imports(root_path, package, dst_path, src_url, progress_callback=None):
    if progress_callback:
        progress_callback()
    try:
        resp = requests.get(src_url, timeout=60 * 2)
        filelike = io.BytesIO(resp.content)
        harvested_data = harvest_imports(filelike)
        with open(
                expand_file_and_mkdirs(os.path.join(root_path, package, dst_path)), "w"
        ) as fo:
            json.dump(harvested_data, fo, indent=1, sort_keys=True)
    except Exception as e:
        raise ReapFailure(package, src_url, str(e))
    return harvested_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root_path")
    parser.add_argument(
        "--known-bad-packages",
        help="name of a json file containing a list of urls to be skipped",
    )

    args = parser.parse_args()
    print(args)
    if args.known_bad_packages:
        with open(args.known_bad_packages, "r") as fo:
            known_bad_packages = set(json.load(fo))
    else:
        known_bad_packages = set()

    reap(args.root_path, known_bad_packages, reap_imports, number_to_reap=10)
