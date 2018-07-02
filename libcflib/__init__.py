"""The libcflib package."""
# setup xonsh
from xonsh.main import setup

setup(shell_type="none")
del setup

# setup environment
from libcflib.environ import setup

setup()
del setup


__version__ = '0.0.2'
