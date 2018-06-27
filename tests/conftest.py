import pytest


@pytest.fixture
def tmpgraphdir(tmpdir_factory):
    d = tmpdir_factory.mktemp("graph", numbered=False)
    d.mkdir("artifacts").mkdir("mypkg").mkdir("/somechannel").mkdir("noarch")
    return d
