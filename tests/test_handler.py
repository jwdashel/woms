import json
import os
import pytest

from argparse import Namespace

from whatsonms.handler import handler, Response

DAVID_SAMPLE = './tests/david_archive_sample.xml'
NEXGEN_SAMPLE_QS = '%0A%3Caudio%20ID%3D%22id_3189206699_30701071%22%3E%0A%3Ctype%3ESong%3C%2Ftype%3E%0A%3Cstatus%3ENone%3C%2Fstatus%3E%0A%3Cplayed_date%3E11%2F06%2F2018%3C%2Fplayed_date%3E%0A%3Cplayed_time%3E15%3A48%3A40%3C%2Fplayed_time%3E%0A%3Clength%3E00%3A03%3A31%3C%2Flength%3E%0A%3Ctitle%3EI%20Concentrate%20On%20You%3C%2Ftitle%3E%0A%3Ccomposer%3ESteve%20Lawrence%3C%2Fcomposer%3E%0A%3Cnumber%3E978416%3C%2Fnumber%3E%0A%3C%2Faudio%3E%0A'


@pytest.fixture
def fake_david_update():
    yield eval(David.get(sample_file=DAVID_SAMPLE))

@pytest.fixture
def fake_nexgen_update():
    yield eval(NexGen.get(NEXGEN_SAMPLE_QS))


class David:
    @staticmethod
    def get(sample_file=None, body=None):
        """ Simulate a request from David with new metadata
        """
        if sample_file:
            with open(sample_file, 'rb') as body:
                return handler(
                    {'body': body, 'httpMethod': 'POST', 'path': '/update'}, {}
                )

        return handler(
            {'body': body, 'httpMethod': 'POST', 'path': '/update'}, {}
        )


class NexGen:
    @staticmethod
    def get(query_string_parameters):
        """ Simulate a request from NexGen with new metadata
        """
        return handler(
            {
                'queryStringParameters': {
                    'xml_contents': query_string_parameters
                },
                'httpMethod': 'GET',
                'path': '/update'
            }, {}
        )


class WebClient:
    @staticmethod
    def get():
        """ Simulate a request from a web client for latest "whats on" metadata
        """
        return handler({'httpMethod': 'GET', 'path': '/whats-on'}, {})


class TestHandler:

    @pytest.mark.parametrize('query_string_parameters', [''])
    def test_invalid_request_nexgen(self, query_string_parameters):
        json = NexGen.get(query_string_parameters)
        assert json is None

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body):
        json = David.get(body=body)
        assert json is None

    def test_valid_request_nexgen(self, fake_nexgen_update):
        expected_response = '978416'
        assert fake_nexgen_update['mm_uid'] == expected_response

    def test_valid_response_david(self, fake_david_update):
        json = fake_david_update
        expected_response = '126753'
        assert json['mm_uid'] == expected_response

    def test_valid_response_web_client(self, fake_david_update):
        whats_on = json.loads(WebClient.get())
        assert whats_on == fake_david_update

    def test_valid_response_web_client_2(self, fake_nexgen_update):
        whats_on = json.loads(WebClient.get())
        assert whats_on == fake_nexgen_update

    def test_simple(self):
        # This actually imports mockredis as defined in our fixture
        # in tests/conftest.py:
        import redis

        client = redis.StrictRedis(decode_responses=True)
        client.set('foo', 'bar')
        assert client.get('foo').decode('utf-8') == 'bar'
