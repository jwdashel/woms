from argparse import Namespace

import json
import os
import pytest

from whatsonms.handler import handler, Response


class NexGen:
    @staticmethod
    def get(query_string_parameters):
        return handler(
            {
                'queryStringParameters': query_string_parameters,
                'httpMethod': 'GET',
                'path': '/update'
            }, {}
        )


class David:
    @staticmethod
    def get(body):
        return handler(
            {'body': body, 'httpMethod': 'POST', 'path': '/update'}, {}
        )


class WebClient:
    """ Simulate a call from a web client for latest whats on metadata
    """
    @staticmethod
    def get():
        return handler({'httpMethod': 'GET', 'path': '/whats-on'}, {})


DAVID_SAMPLE = open('./tests/david_archive_sample.xml', 'rb')
NEXGEN_SAMPLE_QS = '%0A%3Caudio%20ID%3D%22id_3189206699_30701071%22%3E%0A%3Ctype%3ESong%3C%2Ftype%3E%0A%3Cstatus%3ENone%3C%2Fstatus%3E%0A%3Cplayed_date%3E11%2F06%2F2018%3C%2Fplayed_date%3E%0A%3Cplayed_time%3E15%3A48%3A40%3C%2Fplayed_time%3E%0A%3Clength%3E00%3A03%3A31%3C%2Flength%3E%0A%3Ctitle%3EI%20Concentrate%20On%20You%3C%2Ftitle%3E%0A%3Ccomposer%3ESteve%20Lawrence%3C%2Fcomposer%3E%0A%3Cnumber%3E978416%3C%2Fnumber%3E%0A%3C%2Faudio%3E%0A'


class TestHandler:

    @pytest.mark.parametrize('query_string_parameters', [{'xml_contents': ''}])
    def test_invalid_request_nexgen(self, query_string_parameters):
        print(query_string_parameters)

        j = NexGen.get(query_string_parameters)

        assert j is None

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body):
        j = David.get(body)

        assert j is None

    @pytest.mark.parametrize(
        'query_string_parameters',
        [{'xml_contents': NEXGEN_SAMPLE_QS}]
    )
    def test_valid_request_nexgen(self, query_string_parameters):
        j = json.loads(NexGen.get(query_string_parameters))

        print('nexgen json = ', j)

        # dynamically create variables from querystring param dict
        # params = Namespace(**path_parameters)

        expected_response = '978416'

        assert j['mm_uid'] == expected_response

    @pytest.mark.parametrize('body', [DAVID_SAMPLE])
    def test_valid_response_david(self, body):
        j = json.loads(David.get(body))
        DAVID_SAMPLE.close()
        print('david json = ', j)

        # dynamically create variables from querystring param dict
        # params = Namespace(**path_parameters)

        expected_response = '126753'

        assert j['mm_uid'] == expected_response

    @pytest.mark.parametrize(
        'query_string_parameters',
        [{'xml_contents': NEXGEN_SAMPLE_QS}]
    )
    def test_valid_response_web_client(self, query_string_parameters):
        j = json.loads(NexGen.get(query_string_parameters))
        whats_on = json.loads(WebClient.get())

        assert whats_on == j

    def test_simple(self):
        # This should import mockredis as defined in our fixture
        # in tests/conftest.py:
        import redis

        client = redis.StrictRedis(decode_responses=True)
        client.set('foo', 'bar')

        assert client.get('foo').decode('utf-8') == 'bar'
