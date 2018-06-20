"""Main function for libcflib REST API server."""
import argparse

import tornado.web
import tornado.ioloop

import libcflib.rest.handlers
from libcflib.db import DB
from libcflib.logger import LOGGER
from libcflib.rest.request_handler import RequestHandler


def make_parser():
    """Makes and argument parser for fixie."""
    p = argparse.ArgumentParser(
        "libcflib-rest", description="REST API server for libcflib"
    )
    p.add_argument(
        "-p",
        "--port",
        default=8888,
        dest="port",
        type=int,
        help="port to serve the fixie services on.",
    )
    p.add_argument(
        "--no-init-db",
        default=True,
        dest="init_db",
        action="store_false",
        help="turns off database initialization",
    )
    return p


def run_application(ns):
    """Starts up an application with the loaded handlers."""
    # first, find the request handler
    handlers = []
    for var in vars(libcflib.rest.handlers).values():
        if (
            isinstance(var, type)
            and var is not RequestHandler
            and issubclass(var, RequestHandler)
        ):
            handlers.append((var.route, var))
    # init the database
    if ns.init_db:
        DB()
    # construct the app
    app = tornado.web.Application(handlers)
    app.listen(ns.port)
    data = vars(ns)
    url = "http://localhost:" + str(ns.port)
    LOGGER.log("starting libcflib-rest " + url, category="rest-server", data=data)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print()
    LOGGER.log("stopping libcflib-rest " + url, category="rets-server", data=data)


def main(args=None):
    p = make_parser()
    ns = p.parse_args(args)
    ns.args = args
    run_application(ns)


if __name__ == "__main__":
    main()
