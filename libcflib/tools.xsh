"""Varied and sundry tools for libcflib"""
import os
from contextlib import contextmanager

from collections import defaultdict
from collections.abc import MutableMapping

import jinja2
try:
    from conda_build.config import Config
    from conda_build.metadata import parse
except ImportError:
    pass
from xonsh.tools import expand_path


def expand_file_and_mkdirs(x):
    """Expands a variable that represents a file, and ensures that the
    directory it lives in actually exists.
    """
    x = os.path.abspath(expand_path(x))
    d = os.path.dirname(x)
    os.makedirs(d, exist_ok=True)
    return x


def expand_and_make_dir(x):
    """Expands a variable that represents a directory, and ensures that the
    directory actually exists.
    """
    x = os.path.abspath(expand_path(x))
    os.makedirs(x, exist_ok=True)
    return x


def is_non_string_non_dict_iter(x):
    if isinstance(x, str):
        return False
    elif isinstance(x, MutableMapping):
        return False
    elif hasattr(x, "__iter__"):
        return True
    else:
        return False


class NullUndefined(jinja2.Undefined):
    def __unicode__(self):
        return self._undefined_name

    def __getattr__(self, name):
        return '{}.{}'.format(self, name)

    def __getitem__(self, name):
        return '{}["{}"]'.format(self, name)


def render_meta_yaml(text):
    """Render the meta.yaml with Jinja2 variables.

    Parameters
    ----------
    text : str
        The raw text in conda-forge feedstock meta.yaml file

    Returns
    -------
    str
        The text of the meta.yaml with Jinja2 variables replaced.

    """

    env = jinja2.Environment(undefined=NullUndefined)
    content = env.from_string(text).render(
        os=os,
        environ=defaultdict(str),
        compiler=lambda x: x + '_compiler_stub',
        pin_subpackage=lambda *args, **kwargs: 'subpackage_stub',
        pin_compatible=lambda *args, **kwargs: 'compatible_pin_stub',
        cdt=lambda *args, **kwargs: 'cdt_stub', )
    return content


def parse_meta_yaml(text):
    """Parse the meta.yaml.

    Parameters
    ----------
    text : str
        The raw text in conda-forge feedstock meta.yaml file

    Returns
    -------
    dict :
        The parsed YAML dict. If parseing fails, returns an empty dict.

    """

    try:
        content = render_meta_yaml(text)
        return parse(content, Config())
    except:
        return {}


@contextmanager
def indir(d):
    """Context manager for temporarily entering into a directory."""
    old_d = os.getcwd()
    ![cd @(d)]
    yield
    ![cd @(old_d)]