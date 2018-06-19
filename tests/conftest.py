import pytest


@pytest.fixture
def tmppkgdir(tmpdir_factory):
    d = tmpdir_factory.mktemp("mypkg", numbered=False)
    d.mkdir("/somechannel").mkdir("noarch")
    return d
