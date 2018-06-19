"""
Generate a list of artifacts to write to an output of some kind for further processing
"""

import json
import bz2
import io
import os
import glob
from collections import Counter, defaultdict
from typing import Dict, Set

from concurrent.futures import as_completed, ThreadPoolExecutor, wait

import requests
import tqdm

from .harvester import harvest
from .tools import expand_file_and_mkdirs


channel_list = [
    'https://conda.anaconda.org/conda-forge/linux-64',
    'https://conda.anaconda.org/conda-forge/osx-64',
    'https://conda.anaconda.org/conda-forge/win-64',
    'https://conda.anaconda.org/conda-forge/noarch',
]


def fetch_arch(arch):
    # Generate a set a urls to generate for an channel/arch combo
    r = requests.get(f'{arch}/repodata.json.bz2')
    repodata = json.load(bz2.BZ2File(io.BytesIO(r.content)))
    for p, v in repodata['packages'].items():
        package_url = f'{arch}/{p}'
        file_name = (
            package_url
            .replace('https://conda.anaconda.org/', '')
            .replace('.tar.bz2', '.json'))
        yield v['name'], file_name, package_url


def fetch_upstream() -> Dict[str, Dict[str, str]]:
    package_urls = defaultdict(dict)
    for channel_arch in channel_list:
        for package_name, filename, url in fetch_arch(channel_arch):
            package_urls[package_name][filename] = url
    return package_urls


def recursive_ls(root):
    packages = os.listdir(root)
    for p in packages:
        files = glob.glob(f'{root}/{p}/*/*/*.json')
        for f in files:
            yield p, f.replace(f'{root}/{p}/', '')


def existing(path, recursive_ls=recursive_ls) -> Dict[str, Set[str]]:
    existing_dict = defaultdict(set)
    for pak, path in recursive_ls(path):
        existing_dict[pak].add(path)
    return existing_dict


def diff(path):
    missing_files = set()
    upstream = fetch_upstream()
    local = existing(path)

    missing_packages = set(upstream.keys()) - set(local.keys())
    present_packages = set(upstream.keys()) & set(local.keys())

    for package in missing_packages:
        missing_files.update((package, k, v) for k, v in upstream[package].items())

    for package in present_packages:
        upstream_artifacts = upstream[package]
        present_artifacts = local[package]

        missing_artifacts = set(upstream_artifacts) - set(present_artifacts)
        missing_files.update((package, k, v) for k, v in upstream_artifacts.items() if k in missing_artifacts)

    return missing_files


def reap_package(root_path, package, dst_path, src_url, progress_callback=None):
    resp = requests.get(src_url, timeout=60 * 2)
    filelike = io.BytesIO(resp.content)
    harvested_data = harvest(filelike)
    with open(expand_file_and_mkdirs(os.path.join(root_path, package, dst_path)), 'w') as fo:
        json.dump(harvested_data, fo, indent=1, sort_keys=True)
    if progress_callback:
        progress_callback()


def reap(path):
    sorted_files = list(sorted(diff(path)))
    progress = tqdm.tqdm(total=len(sorted_files))
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [pool.submit(
            reap_package, path, package, dst, src_url, progress_callback=progress.update) for
                package, dst, src_url in sorted_files
        ]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(str(e))
                raise


if __name__ == '__main__':
    reap('/Users/mvanniekerk/src/conda-forge/libcfgraph/artifacts')
