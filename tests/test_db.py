import pytest
from libcflib import db


@pytest.fixture(scope="session")
def db_fixture(tmpgraphdir, gitecho):
    return db.DB()


def test_load_packages(db_fixture):
    db_fixture.load_packages()


def test_search(db_fixture, tmpgraphindex, documents):
    res = list(db_fixture.search({}))
    assert len(res) == 3
    res = list(db_fixture.search({"a": 3}))
    assert len(res) == 2
    res = list(db_fixture.search({"a": 3, "b": 5}))
    assert len(res) == 1
