from argparse import Namespace

import json
import os
import pytest

from whatsonms.handler import handler, Response


class client1:
    @staticmethod
    def get(query_string_parameters):
        return handler({'queryStringParameters': query_string_parameters, 'httpMethod': 'GET'}, {})

class client2:
    @staticmethod
    def get(body):
        return handler({'body': body, 'httpMethod': 'POST'}, {})


DAVID_SAMPLE = open('./tests/david_archive_sample.xml', 'rb')


class TestHandler:

    @pytest.mark.parametrize(
        'query_string_parameters',
        [
            {
                'xml_contents': ''
            }
        ]
    )
    def test_invalid_request_client1(self, query_string_parameters):
        print(query_string_parameters)

        j = client1.get(query_string_parameters)

        assert j is None

    @pytest.mark.parametrize(
        'body',
        [
            {}
        ]
    )
    def test_invalid_request_client2(self, body):
        j = client2.get(body)

        assert j is None

    @pytest.mark.parametrize(
        'query_string_parameters',
        [
            {
                'xml_contents': '%0A%3Caudio%20ID%3D%22id_3189206699_30701071%22%3E%0A%3Ctype%3ESong%3C%2Ftype%3E%0A%3Cstatus%3ENone%3C%2Fstatus%3E%0A%3Cplayed_date%3E11%2F06%2F2018%3C%2Fplayed_date%3E%0A%3Cplayed_time%3E15%3A48%3A40%3C%2Fplayed_time%3E%0A%3Clength%3E00%3A03%3A31%3C%2Flength%3E%0A%3Ctitle%3EI%20Concentrate%20On%20You%3C%2Ftitle%3E%0A%3Ccomposer%3ESteve%20Lawrence%3C%2Fcomposer%3E%0A%3Cnumber%3E978416%3C%2Fnumber%3E%0A%3C%2Faudio%3E%0A'
            }
        ]
    )
    def test_valid_request_client1(self, query_string_parameters):
        j = json.loads(client1.get(query_string_parameters))

        # dynamically create variables from querystring param dict
        # params = Namespace(**path_parameters)

        expected_response = 'id_3189206699_30701071'

        assert j['audio']['@ID'] == expected_response

    @pytest.mark.parametrize(
        'body',
        [
            DAVID_SAMPLE
        ]
    )
    def test_valid_response_client2(self, body):
        j = json.loads(client2.get(body))

        # dynamically create variables from querystring param dict
        # params = Namespace(**path_parameters)

        expected_response = '109921'

        assert j['wddxPacket']['item'][0]['Music_MusicID'] == expected_response
