import pathlib

from libcflib.expose_data import CachedData


def test_get_import_map(tmpdir):
    cd = CachedData(session_kwargs={
        'cache_name': str(pathlib.Path(tmpdir) / pathlib.Path('.config/libcflib/cache_session.sqlite')),
        'backend': 'sqlite',
        'exire_after': 60*60*1
    })
    first_two_letters = 'ma'
    data = cd.get_import_map(first_two_letters)
    assert 'matplotlib' in data
    url = cd.IMPORT_MAP_URL_TEMPLATE.format(import_first_two_letters=first_two_letters)
    assert cd.session.cache.has_url(url)
