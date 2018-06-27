"""A request handler for libcflib that expects JSON data and validates it."""
import cerberus

import tornado.web
from tornado.escape import utf8

from libcflib.db import DB
import libcflib.jsonutils as json


class RequestHandler(tornado.web.RequestHandler):
    """A Tornado request handler that prepare the data by loading a
    JSON request and then validating the resultant object against
    the cerberus schema defined on the class as the 'schema' attribute.
    This class is meant to be subclassed.
    """

    _db = None
    route = None

    @property
    def validator(self):
        v = getattr(self.__class__, "_validator", None)
        if v is None:
            v = cerberus.Validator(self.schema)
            self.__class__._validator = v
        return v

    @property
    def db(self):
        """Gets the database object"""
        if self._db is None:
            self._db = DB()
        return self._db

    def prepare(self):
        self.response = {}
        body = self.request.body
        if body:
            try:
                data = json.decode(body)
            except ValueError:
                self.send_error(400, message="Unable to parse JSON.")
                return
        else:
            # tornado returns values as list. Take the last entry
            # to conform to the JSON schema. Also, need to decode the values
            data = {k: v[-1].decode() for k, v in self.request.arguments.items()}
        if not self.validator.validate(data):
            msg = "Input to " + self.__class__.__name__ + " is not valid: "
            msg += str(self.validator.errors)
            self.send_error(400, message=msg)
            return
        self.data = data

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def write(self, chunk):
        """Writes the given chunk to the output buffer. This overrides (and almost
        completely reimplements) tornado.web.RequestHandler.write() so that we
        can use the default libcflic JSON tools.
        """
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, str, dict)) and not hasattr(chunk, "asdict"):
            message = "write() only accepts bytes, unicode, and dict objects"
            if isinstance(chunk, list):
                message += (
                    ". Lists not accepted for security reasons; see "
                    "http://www.tornadoweb.org/en/stable/web.html"
                    "#tornado.web.RequestHandler.write"
                )
            raise TypeError(message)
        if isinstance(chunk, dict) or hasattr(chunk, "asdict"):
            chunk = json.encode(chunk) + "\n"
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)

    def write_error(self, status_code, **kwargs):
        if "message" not in kwargs:
            if status_code == 405:
                kwargs["message"] = "Invalid HTTP method."
            else:
                kwargs["message"] = "Unknown error."
        self.response = kwargs
        self.write(kwargs)
