import contextlib
import glob
import io
import json
import os
import tarfile
import traceback
from concurrent.futures._base import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from tempfile import TemporaryDirectory


import requests
from libcflib.tools import expand_file_and_mkdirs
from tqdm import tqdm

from libcflib.preloader import ReapFailure, diff
import psutil


@contextlib.contextmanager
def executor(kind: str, max_workers: int, daemon=True):
    """General purpose utility to get an executor with its as_completed handler

    This allows us to easily use other executors as needed.
    """
    if kind == "thread":
        with ThreadPoolExecutor(max_workers=max_workers) as pool_t:
            yield pool_t
    elif kind == "process":
        with ProcessPoolExecutor(max_workers=max_workers) as pool_p:
            yield pool_p
    elif kind in ["dask", "dask-process", "dask-thread"]:
        import dask
        import distributed
        from distributed.cfexecutor import ClientExecutor

        processes = kind == "dask" or kind == "dask-process"

        with dask.config.set({"distributed.worker.daemon": daemon}):
            with distributed.LocalCluster(
                n_workers=max_workers,
                processes=processes,
            ) as cluster:
                with distributed.Client(cluster) as client:
                    yield ClientExecutor(client)
    else:
        raise NotImplementedError("That kind is not implemented")


def file_path_to_import(file_path: str):
    return file_path.replace("/__init__.py", "").replace(".py", "").replace("/", ".")


class bla:
    full_name='hi'
    type='hi'


def get_all_symbol_names(top_dir):
    import jedi.settings

    jedi.settings.fast_parser = False

    from jedi.cache import clear_time_caches
    import jedi
    # Note Jedi seems to pick up things that are protected by a
    # __name__ == '__main__' if statement
    # this could cause some over-reporting of viable imports this
    # shouldn't cause issues with an audit since we don't expect 3rd parties
    # to depend on those
    symbols_dict = {}
    errors_dict = {}
    # walk all the files looking for python files
    glob_glob = glob.glob(f'{top_dir}/**/*.py', recursive=True)
    for file_name in [k for k in glob_glob]:
        # TODO: check for `__init__.py` existence or that the file is top level
        folder_path = file_name.rpartition(top_dir + '/')[-1]
        import_name = file_path_to_import(folder_path)
        module_import = import_name.split('.')[0]
        try:
            data = jedi.Script(path=file_name, project=jedi.Project(''.join(top_dir))).complete()
            # data = [bla] * 100
        except Exception as e:
            print(import_name)
            errors_dict[import_name] = {
                "exception": str(e),
                "traceback": str(traceback.format_exc()).split(
                    "\n",
                ),
            }
            data = []

        symbols_from_script = {
            k.full_name: k.type
            for k in data
            # Checks that the symbol has a name and comes from the pkg in question
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
        del data
        del symbols_from_script

    # try to fix bad jedi memory leak
    clear_time_caches(True)

    symbols = set()
    # handle star imports, which don't usually get added but are valid symbols
    for k, v in symbols_dict.items():
        symbols.update(v)
        symbols.update({f"{k}.{vv.rsplit('.', 1)[-1]}" for vv in v})
    del symbols_dict
    return symbols, errors_dict


def harvest_imports(io_like):
    tf = tarfile.open(fileobj=io_like, mode="r:bz2")
    # TODO: push dir allocation into thread
    with TemporaryDirectory() as f:
        tf.extractall(path=f)
        symbols = set()
        errors = {}
        found_sp = False
        for root, subdirs, files in os.walk(f):
            if root.lower().endswith('site-packages'):
                found_sp = True
                _symbols, _errors = get_all_symbol_names(root)
                symbols.update(_symbols)
                errors.update(_errors)
    tf.close()
    output = dict(errors=errors, symbols=sorted(symbols))
    if not found_sp:
        return None
    return output


def reap_imports(root_path, package, dst_path, src_url,
                 filelike,
                 progress_callback=None):
    if progress_callback:
        progress_callback()
    try:
        harvested_data = harvest_imports(filelike)
        with open(
                expand_file_and_mkdirs(os.path.join(root_path, package, dst_path)), "w"
        ) as fo:
            json.dump(harvested_data, fo, indent=1, sort_keys=True)
        del harvested_data
    except Exception as e:
        raise ReapFailure(package, src_url, str(e))
    # return harvested_data


def fetch_artifact(src_url):
    resp = requests.get(src_url, timeout=60 * 2)
    filelike = io.BytesIO(resp.content)
    return filelike


def fetch_and_run(path, pkg, dst, src_url, progess_callback=None):
    print('hi')
    filelike = fetch_artifact(src_url)
    print('fetched')
    reap_imports(path, pkg, dst, src_url, filelike, progress_callback=progess_callback)
    print('reaped')


def reap(path, known_bad_packages=(), reap_function=reap_imports, number_to_reap=1000,
         ):
    if not os.path.exists(path):
        os.makedirs(path)
    sorted_files = list(diff(path))
    print(f"TOTAL OUTSTANDING ARTIFACTS: {len(sorted_files)}")
    sorted_files = sorted_files[:number_to_reap]
    # progress = tqdm(total=len(sorted_files))

    # with ThreadPoolExecutor(max_workers=20) as pool:
    #     futures = {pool.submit(fetch_artifact, src_url): (package, dst, src_url)
    #                for package, dst, src_url in sorted_files
    #                if (src_url not in known_bad_packages)}
    #     for f in as_completed(futures):
    #         try:
    #             initial = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    #             package, dst, src_url = futures.pop(f)
    #             reap_function(path, package, dst, src_url, f.result(),
    #                           progress_callback=progress.update,
    #                           )
    #             del f
    #             print(initial, psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)
    #         except ReapFailure as e:
    #             print(f"FAILURE {e.args}")
    #         except Exception:
    #             pass

    with executor(max_workers=3, kind='dask') as pool:
        futures = {pool.submit(fetch_and_run, path, package, dst, src_url,
                               # progress.update
                               ): (package, dst, src_url)
                   for package, dst, src_url in sorted_files
                   if (src_url not in known_bad_packages)}
        for f in as_completed(futures):
            try:
                initial = psutil.virtual_memory().available / 1024 ** 2
                f.result()
                print(initial, psutil.virtual_memory().available / 1024 **2)
            except ReapFailure as e:
                print(f"FAILURE {e.args}")
            except Exception:
                pass

    # for package, dst, src_url in sorted_files:
    #     if (src_url in known_bad_packages):
    #         continue
    #     f = fetch_artifact(src_url)
    #     try:
    #         reap_function(path, package, dst, src_url, f,
    #                       progress_callback=progress.update,
    #                       )
    #     except ReapFailure as e:
    #         print(f"FAILURE {e.args}")
    #     except Exception:
    #         pass

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
    reap(args.root_path, known_bad_packages, reap_imports, number_to_reap=100)
