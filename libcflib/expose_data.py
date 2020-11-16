import pathlib
from requests_cache import CachedSession
from ruamel import yaml


class CachedData:
    IMPORT_MAP_URL_TEMPLATE = "https://raw.githubusercontent.com/regro/libcfgraph/master/import_maps/{import_first_two_letters}.json"
    FILE_LISTING_URL = (
        "https://raw.githubusercontent.com/regro/libcfgraph/master/.file_listing.json"
    )
    HUBS_AUTHS_URL = "https://raw.githubusercontent.com/regro/cf-graph-countyfair/master/ranked_hubs_authorities.json"
    DEFAULT_SESSION_SETTINGS = {
        "cache_name": str(
            pathlib.Path("~/.config/libcflib/cache_session.sqlite").absolute()
        ),
        "backend": "sqlite",
        "exire_after": 60 * 60 * 1,
    }

    def __init__(self, session_kwargs=None):
        if session_kwargs is None:
            p = pathlib.Path("~/.config/libcflib/cache_session_kwargs.yaml").absolute()
            if p.exists():
                session_kwargs = yaml.load(p.open())
            else:
                session_kwargs = {}
        _session_kwargs = self.DEFAULT_SESSION_SETTINGS.copy()
        _session_kwargs.update(session_kwargs)
        p = pathlib.Path(_session_kwargs["cache_name"])
        p.mkdir(parents=True, exist_ok=True)
        p.touch()
        self.session = CachedSession(**_session_kwargs)

    def _get(self, url):
        return self.session.get(url).json()

    def get_import_map(self, first_two_letters):
        return self._get(
            self.IMPORT_MAP_URL_TEMPLATE.format(
                import_first_two_letters=first_two_letters
            )
        )
