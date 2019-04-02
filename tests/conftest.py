import json
import urllib.parse

import pytest
from moto import mock_dynamodb2

from whatsonms.config import DYNAMODB_TABLE, URL_PREFIX

WQXR_STREAM_SLUG = 'wqxr'


@pytest.fixture(autouse=True)
def handler(mocker):
    with mock_dynamodb2():
        from whatsonms.dynamodb import DB
        import whatsonms.handler
        DB(DYNAMODB_TABLE)
        yield whatsonms.handler


@pytest.fixture
def mock_david(handler):

    def event_dict(body):
        return {
            'body': body,
            'httpMethod': 'POST',
            'path': URL_PREFIX + '/v1/update',
            'queryStringParameters': {
                'stream': WQXR_STREAM_SLUG
            },
        }

    def get(sample_file=None, body=None):
        """ Simulate a request from David with new metadata
        """
        if sample_file:
            with open(sample_file, 'rb') as body:
                resp = handler(event_dict(body), {})
        else:
            resp = handler(event_dict(body), {})
        return json_from_str(resp)

    yield get


@pytest.fixture
def mock_nexgen(handler):

    def get(qs_params):
        """ Simulate a request from NexGen with new metadata
        """
        resp = handler({
            'httpMethod': 'GET',
            'path': URL_PREFIX + '/v1/update',
            'queryStringParameters': {
                'stream': WQXR_STREAM_SLUG,
                'xml_contents': urllib.parse.unquote(qs_params)
            },
        }, {})
        return json_from_str(resp)

    yield get


@pytest.fixture
def mock_web_client(handler):

    def get(stream_slug=WQXR_STREAM_SLUG):
        """ Simulate a request from a web client for latest "whats on" metadata
        """
        resp = handler({
            'httpMethod': 'GET',
            'path': URL_PREFIX + '/v1/whats-on',
            'queryStringParameters': {
                'stream': stream_slug
            },
        }, {})
        return json_from_str(resp)
    yield get


def json_from_str(obj):
    return json.loads(obj) if isinstance(obj, str) else obj
