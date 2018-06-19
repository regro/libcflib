import pytest
from libcflib import db


@pytest.fixture(scope="session")
def db_fixture():
    return db.DB()


def test_load_packages(db_fixture):
    db_fixture.load_packages()
