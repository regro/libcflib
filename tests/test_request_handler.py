"""Tests libcflib handler object."""
import pytest

import tornado.web
from tornado.httpclient import HTTPError

from libcflib.rest.request_handler import RequestHandler


class ValidationRequest(RequestHandler):

    schema = {'name': {'type': 'string'}}

    def post(self):
        name = self.request.arguments['name']
        self.write('My name is ' + name)


APP = tornado.web.Application([
    (r"/", ValidationRequest),
])


@pytest.fixture
def app():
    return APP


@pytest.mark.gen_test
def test_valid(http_client, base_url):
    body = '{"name": "Inigo Montoya"}'
    response = yield http_client.fetch(base_url, method="POST", body=body)
    assert response.code == 200
    assert response.body == b'My name is Inigo Montoya'


@pytest.mark.gen_test
def test_invalid(http_client, base_url):
    body = '{"name": 42}'
    try:
        response = yield http_client.fetch(base_url, method="POST", body=body)
    except HTTPError as e:
        response = e.response
    assert response.code == 400
    assert b'not valid' in response.body


@pytest.mark.gen_test
def test_not_json(http_client, base_url):
    body = '"name": 42'
    try:
        response = yield http_client.fetch(base_url, method="POST", body=body)
    except HTTPError as e:
        response = e.response
    assert response.code == 400
    assert b'Unable to parse JSON.' in response.body
