import pytest
from libcflib import db


@pytest.fixture(scope="session")
def db_fixture(tmpgraphdir, gitecho):
    return db.DB()


def test_load_packages(db_fixture):
    db_fixture.load_packages()


def test_search(db_fixture, tmpgraphindex, documents):
    res = list(db_fixture.search({}))
    assert all(doc in res for doc in documents)
    res = list(db_fixture.search({'a': 3}))
    assert all(documents[i] in res for i in [0, 1])
    assert documents[2] not in res
    res = list(db_fixture.search({'a': 3, 'b': 5}))
    assert documents[0] in res
    assert all(documents[i] not in res for i in [1, 2])
