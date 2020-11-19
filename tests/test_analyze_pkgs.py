import json
from pathlib import Path

import pytest

from libcflib.analyze_pkgs import file_path_to_import, get_imports

STREAMZ_IMPORTS = {'streamz', 'streamz.batch', 'streamz.collection', 'streamz.compatibility', 'streamz.core',
                   'streamz.dask', 'streamz.dataframe', 'streamz.dataframe.aggregations', 'streamz.dataframe.core',
                   'streamz.dataframe.utils', 'streamz.graph', 'streamz.orderedweakset', 'streamz.sources',
                   'streamz.tests', 'streamz.tests.py3_test_core', 'streamz.tests.test_batch',
                   'streamz.tests.test_core', 'streamz.tests.test_dask', 'streamz.tests.test_graph',
                   'streamz.tests.test_kafka', 'streamz.tests.test_sources', 'streamz.utils', 'streamz.utils_test'}

STREAMZ_FILES = [
    "site-packages/streamz-0.6.1.dist-info/INSTALLER",
    "site-packages/streamz-0.6.1.dist-info/METADATA",
    "site-packages/streamz-0.6.1.dist-info/RECORD",
    "site-packages/streamz-0.6.1.dist-info/REQUESTED",
    "site-packages/streamz-0.6.1.dist-info/WHEEL",
    "site-packages/streamz-0.6.1.dist-info/direct_url.json",
    "site-packages/streamz-0.6.1.dist-info/pbr.json",
    "site-packages/streamz/__init__.py",
    "site-packages/streamz/batch.py",
    "site-packages/streamz/collection.py",
    "site-packages/streamz/compatibility.py",
    "site-packages/streamz/core.py",
    "site-packages/streamz/dask.py",
    "site-packages/streamz/dataframe/__init__.py",
    "site-packages/streamz/dataframe/aggregations.py",
    "site-packages/streamz/dataframe/core.py",
    "site-packages/streamz/dataframe/tests/test_dataframe_utils.py",
    "site-packages/streamz/dataframe/tests/test_dataframes.py",
    "site-packages/streamz/dataframe/utils.py",
    "site-packages/streamz/graph.py",
    "site-packages/streamz/orderedweakset.py",
    "site-packages/streamz/sources.py",
    "site-packages/streamz/tests/__init__.py",
    "site-packages/streamz/tests/py3_test_core.py",
    "site-packages/streamz/tests/test_batch.py",
    "site-packages/streamz/tests/test_core.py",
    "site-packages/streamz/tests/test_dask.py",
    "site-packages/streamz/tests/test_graph.py",
    "site-packages/streamz/tests/test_kafka.py",
    "site-packages/streamz/tests/test_sources.py",
    "site-packages/streamz/utils.py",
    "site-packages/streamz/utils_test.py"
]

FILE_IMPORT = [
    ('Lib/site-packages/AnyPyTools-0.9.4-py3.5.egg/anypytools/h5py_wrapper.py',
     'anypytools.h5py_wrapper'),
    ('lib/python3.9/site-packages/scipy/integrate/lsoda.cpython-39-x86_64-linux-gnu.so',
     'scipy.integrate.lsoda'),
    ('lib/python3.9/site-packages/scipy/integrate/odepack.py',
     'scipy.integrate.odepack'),
    ('lib/python3.7/site-packages/tests/common/test_hashing.py',
     'tests.common.test_hashing'),
    ("site-packages/pandas/_libs/algos.so", None),
    ('lib/python3.7/site-packages/foo.py', 'foo'),
    ('Lib/site-packages/dipy/align/bundlemin.cp38-win_amd64.pyd', 'dipy.align.bundlemin'),
    ('lib/python3.6/site-packages/numpy/linalg/lapack_lite.pypy36-pp73-x86_64-linux-gnu.so', 'numpy.linalg.lapack_lite'),
    ('lib/python3.9/site-packages/zstd.cpython-39-x86_64-linux-gnu.so', 'zstd')
]


@pytest.mark.parametrize('i, o', FILE_IMPORT)
def test_file_path_to_import(i, o):
    assert file_path_to_import(i) == o


def test_get_imports(tmpdir):
    fn = Path(tmpdir, 'imports.json')
    with open(fn, 'w') as f:
        json.dump({'files': STREAMZ_FILES}, f)
    assert get_imports(str(fn)) == STREAMZ_IMPORTS
