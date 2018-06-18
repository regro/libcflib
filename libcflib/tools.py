"""Varied and sundry tools for libcflib"""
import os

from xonsh.tools import expand_path


def expand_file_and_mkdirs(x):
    """Expands a variable that represents a file, and ensures that the
    directory it lives in actually exists.
    """
    x = os.path.abspath(expand_path(x))
    d = os.path.dirname(x)
    os.makedirs(d, exist_ok=True)
    return x
