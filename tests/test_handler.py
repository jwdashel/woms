import json
import os
import pytest

from argparse import Namespace



DAVID_SAMPLE = './tests/david_archive_sample.xml'
NEXGEN_SAMPLE_QS = '%0A%3Caudio%20ID%3D%22id_3189206699_30701071%22%3E%0A%3Ctype%3ESong%3C%2Ftype%3E%0A%3Cstatus%3ENone%3C%2Fstatus%3E%0A%3Cplayed_date%3E11%2F06%2F2018%3C%2Fplayed_date%3E%0A%3Cplayed_time%3E15%3A48%3A40%3C%2Fplayed_time%3E%0A%3Clength%3E00%3A03%3A31%3C%2Flength%3E%0A%3Ctitle%3EI%20Concentrate%20On%20You%3C%2Ftitle%3E%0A%3Ccomposer%3ESteve%20Lawrence%3C%2Fcomposer%3E%0A%3Cnumber%3E978416%3C%2Fnumber%3E%0A%3C%2Faudio%3E%0A'

class TestHandler:

    @pytest.mark.parametrize('query_string_parameters', [''])
    def test_invalid_request_nexgen(self, query_string_parameters, mock_nexgen):
        resp = mock_nexgen(query_string_parameters)
        assert resp is None

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body, mock_david):
        resp = mock_david(body=body)
        assert resp is None

    def test_valid_request_nexgen(self, mock_nexgen):
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        expected_response = '978416'
        assert mock_update['mm_uid'] == expected_response

    def test_valid_response_david(self, mock_david):
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        expected_response = '126753'
        assert mock_update['mm_uid'] == expected_response

    def test_valid_response_web_client(self, mock_david, mock_web_client):
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        whats_on = mock_web_client()
        assert whats_on == mock_update

    def test_valid_response_web_client_2(self, mock_nexgen, mock_web_client):
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        whats_on = mock_web_client()
        assert whats_on == mock_update
