import pytest


@pytest.fixture
def tmppkgdir(tmpdir_factory):
    d = tmpdir_factory.mktemp("artifacts", numbered=False)
    d.mkdir("mypkg").mkdir("/somechannel").mkdir("noarch")
    return d
