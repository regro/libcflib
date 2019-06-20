import re

from libcflib.tools import parse_meta_yaml

sel_pat = re.compile(".+?\s*(#.*)?\[[^\[\]]+\](?(1)[^\(\)]*)$")
ARCHS = ["linux-32", "linux-64", "linux-arm", "osx-64", "win-32", "win-64"]


def has_selectors(meta_yaml):
    for line in meta_yaml.splitlines():
        line = line.rstrip()
        if line.lstrip().startswith("#"):
            continue
        if sel_pat.match(line):
            return True
    return False


def get_packages_from_recipe(recipe):
    outputs = recipe.get("outputs", recipe["package"])
    packages = set()
    for package in outputs:
        packages.add(package)
    return packages


def extract_packages_from_feedstock(feedstock, arch=None):
    packages = set()
    if not arch and has_selectors(feedstock.meta_yaml):
        for a in ARCHS:
            packages.update(extract_packages_from_feedstock(feedstock, arch=a))
    elif arch:
        return get_packages_from_recipe(parse_meta_yaml(feedstock.meta_yaml, arch=arch))
    else:
        return get_packages_from_recipe(parse_meta_yaml(feedstock.meta_yaml))


def get_feedstock_names():
    git init feedstock
    with indir(feedstocks):
        git remote add origin git@github.com:conda-forge/feedstocks.git
        git config core.sparsecheckout true
        echo "feedstocks/" >> .git/info/sparse-checkout
        git pull --depth=1 origin master
        feedstocks = $(ls feedstocks/).splitlines()
    rm -rf feedstocks
    return feedstocks
