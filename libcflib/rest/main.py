"""Main function for libcflib REST API server."""
import sys
import argparse
import importlib

import tornado.web
import tornado.ioloop

import libcflib.rest.handlers
from libcflib.rest.request_handler import RequestHandler


def make_parser():
    """Makes and argument parser for fixie."""
    p = argparse.ArgumentParser('libcflib-rest',
                                description='REST API server for libcflib')
    p.add_argument('-p', '--port', default=8888, dest='port', type=int,
                   help='port to serve the fixie services on.')
    return p


def run_application(ns):
    """Starts up an application with the loaded handlers."""
    # first, find the request handler
    handlers = []
    for var in vars(libcflib.rest.handlers).values():
        if issubclass(var, RequestHandler):
            handlers.append((var.route, var))
    # construct the app
    app = tornado.web.Application(handlers)
    serv = app.listen(ns.port)
    url = 'http://localhost:' + str(ns.port)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print()


def main(args=None):
    args = sys.argv if args is None else args
    p = make_parser()
    ns = p.parse_args(args)
    ns.args = args
    run_application(ns)


if __name__ == '__main__':
    main()
