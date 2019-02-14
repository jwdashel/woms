import json
import pytest

from mockredis import mock_strict_redis_client

from whatsonms.handler import handler


@pytest.fixture(autouse=True, scope='function')
def mock_redis(mocker):
    redis_client = mocker.patch('redis.StrictRedis', mock_strict_redis_client)
    yield redis_client

@pytest.fixture
def mock_david(mock_redis):

    def event_dict(body):
        return {
            'body': body,
            'httpMethod': 'POST',
            'path': '/update',
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
def mock_nexgen(mock_redis):

    def get(qs_params):
        """ Simulate a request from NexGen with new metadata
        """
        resp = handler({
            'queryStringParameters': {
                'xml_contents': qs_params
            },
            'httpMethod': 'GET',
            'path': '/update',
        }, {})
        return json_from_str(resp)

    yield get

@pytest.fixture
def mock_web_client(mock_redis):
    def get():
        """ Simulate a request from a web client for latest "whats on" metadata
        """
        resp = handler({
            'httpMethod': 'GET',
            'path': '/whats-on',
        }, {})
        return json_from_str(resp)
    yield get

def json_from_str(obj):
    return json.loads(obj) if isinstance(obj, str) else obj
