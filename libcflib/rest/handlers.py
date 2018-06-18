"""REST Specification request handlers."""
from libcflib.rest.request_handler import RequestHandler


NON_EMPTY_STR = {'type': 'string', 'empty': False, 'required': True}


class Artifact(RequestHandler):
    """Gets an artifact's data"""

    route = '/artifact'
    schema = {'package': NON_EMPTY_STR.copy(),
              'channel': NON_EMPTY_STR.copy(),
              'arch': NON_EMPTY_STR.copy(),
              'name': NON_EMPTY_STR.copy(),
              }

    def get(self, *args, **kwargs):
        """GETs an artifact."""

