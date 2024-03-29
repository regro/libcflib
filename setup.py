#!/usr/bin/env python
import os

from setuptools import setup


__version__ = None
pth = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "libcflib",
    "_version.py")
with open(pth, 'r') as fp:
    exec(fp.read())
VERSION = __version__

install_file = os.path.join(os.path.dirname(__file__), "requirements", "run.txt")
with open(install_file) as f:
    install_reqs = f.read()
install_reqs = install_reqs.split()

setup_kwargs = {
    "name": "libcflib",
    "packages": ["libcflib", "libcflib.rest"],
    "package_dir": {
        "libcflib": "libcflib",
        "libcflib.rest": "libcflib/rest",
    },
    "package_data": {
        "libcflib": ["*.xsh"],
        "libcflib.rest": ["*.xsh"],
    },
    "long_description": open("README.md").read(),
    "version": VERSION,
    "description": "Library Conda Forge Library",
    "license": "BSD 3-clause",
    "author": "The Regro developers",
    "author_email": "conda-forge@googlegroups.com",
    "url": "https://github.com/regro/libcflib",
    "download_url": "https://github.com/ergs/conda-forge/zipball/" + VERSION,
    "classifiers": [
        "License :: OSI Approved",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    "zip_safe": False,
    "data_files": [("", ["LICENSE", "README.md"])],
    "scripts": [],
    "install_requires": install_reqs,
}

setup(**setup_kwargs)
