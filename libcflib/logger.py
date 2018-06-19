"""Logging tools for libcflib"""
import os
import time
import builtins

from xonsh.tools import print_color

import libcflib.jsonutils as json
from libcflib.tools import expand_file_and_mkdirs


class Logger:
    """A logging object for fixie that stores information in line-oriented JSON
    format.
    """

    __inst = None

    def __new__(cls):
        # make the logger a singleton
        if Logger.__inst is None:
            Logger.__inst = object.__new__(cls)
        return Logger.__inst

    def __init__(self, filename=None):
        """
        Parameters
        ----------
        filename : str or None, optional
            Path to logfile, if None, defaults to $LIBCFLIB_LOGFILE.
        """
        self._filename = None
        self.filename = filename
        self._dirty = True
        self._cached_entries = ()

    def log(self, message, category="misc", data=None):
        """Logs a message, the timestamp, its category, and the
        and any data to the log file.
        """
        self._dirty = True
        entry = {"message": message, "timestamp": time.time(), "category": category}
        if data is not None:
            entry["data"] = data

        # write to log file
        json.appendline(entry, self.filename)
        # write to stdout
        msg = "{INTENSE_CYAN}" + category + "{PURPLE}:"
        msg += "{INTENSE_WHITE}" + message + "{NO_COLOR}"
        print_color(msg)

    def load(self):
        """Loads all of the records from the logfile and returns a list of dicts.
        If the log file does not yet exist, this returns an empty list.
        """
        if not os.path.isfile(self.filename):
            return []
        if not self._dirty:
            return self._cached_entries
        entries = json.loadlines(self.filename)
        self._dirty = False
        self._cached_entries = entries
        return entries

    @property
    def filename(self):
        value = self._filename
        if value is None:
            value = builtins.__xonsh_env__.get("LIBCFLIB_LOGFILE")
        return value

    @filename.setter
    def filename(self, value):
        if value is None:
            self._filename = value
        else:
            self._filename = expand_file_and_mkdirs(value)


LOGGER = Logger()
