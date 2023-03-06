"""The libcflib package."""
# flake8: noqa
# setup xonsh
from xonsh.main import setup

setup(shell_type="none")
del setup

# setup environment
from libcflib.environ import setup

setup()
del setup

from ._version import __version__
