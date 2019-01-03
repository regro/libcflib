import pytest
from libcflib import db


@pytest.fixture(scope="session")
def db_fixture(tmpgraphdir, gitecho):
    return db.DB()


def test_load_packages(db_fixture):
    db_fixture.load_packages()


def test_search_simple(db_fixture, documents):
    obs = set(db_fixture.search("noarch"))
    exp = {db_fixture.get_artifact(path=doc["path"]) for doc in documents[:2]}
    assert len(obs) == 2
    assert obs == exp


def test_search_pagesize(db_fixture, documents):
    obs = set(db_fixture.search("noarch", page_size=1))
    exp = {db_fixture.get_artifact(path=documents[1]["path"])}
    assert len(obs) == 1
    assert obs == exp


def test_search_pagenum(db_fixture, documents):
    obs = set(db_fixture.search("noarch", page_size=1, page_num=2))
    exp = {db_fixture.get_artifact(path=documents[0]["path"])}
    assert len(obs) == 1
    assert obs == exp
