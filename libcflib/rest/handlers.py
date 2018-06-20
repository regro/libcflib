"""REST Specification request handlers."""
from libcflib.rest.request_handler import RequestHandler


NON_EMPTY_STR = {"type": "string", "empty": False, "required": True}


class Artifact(RequestHandler):
    """Gets an artifact's data"""

    route = "/artifact"
    schema = {
        "pkg": NON_EMPTY_STR.copy(),
        "channel": NON_EMPTY_STR.copy(),
        "arch": NON_EMPTY_STR.copy(),
        "name": NON_EMPTY_STR.copy(),
    }

    def get(self, *args, **kwargs):
        """GETs an artifact."""
        a = self.db.get_artifact(**self.data)
        self.write(a)


class Packages(RequestHandler):
    """Gets the packages dictionary"""

    route = "/packages"
    schema = {}

    def get(self, *args, **kwargs):
        """GETs the packages dict"""
        self.write(self.db.packages)


class Package(RequestHandler):
    """Gets the packages dictionary"""

    route = "/package"
    schema = {"pkg": NON_EMPTY_STR.copy()}

    def get(self, *args, **kwargs):
        """GETs the packages dict"""
        self.write(self.db.packages[self.data("pkg")])
