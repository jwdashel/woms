import json
import pytest
from urllib import parse


DAVID_SAMPLE = './tests/david_archive_sample.xml'
NEXGEN_SAMPLE_XML = """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_date>11/06/2018</played_date>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>I Concentrate On You</title>
<composer>Steve Lawrence</composer>
<number>978416</number>
</audio>
"""
NEXGEN_SAMPLE_QS = parse.quote(NEXGEN_SAMPLE_XML, safe=())


class TestHandler:

    @pytest.mark.parametrize('qs_parameters', [''])
    def test_invalid_request_nexgen(self, qs_parameters, mock_nexgen):
        resp = mock_nexgen(qs_parameters)
        assert resp['statusCode'] == 404

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body, mock_david):
        resp = mock_david(body=body)
        assert resp['statusCode'] == 404

    def test_valid_request_nexgen(self, mock_nexgen):
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        expected_response = '978416'
        response_body = json.loads(mock_update['body'])
        assert response_body['data']['attributes']['mm_uid'] == \
            expected_response

    def test_valid_request_david(self, mock_david):
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        expected_response = '126753'
        response_body = json.loads(mock_update['body'])
        assert response_body['data']['attributes']['mm_uid'] == \
            expected_response

    def test_invalid_request_web_client(self, mock_web_client):
        resp = mock_web_client(stream_slug='foobar')
        assert resp['statusCode'] == 404

    def test_valid_request_web_client(self, mock_david, mock_web_client):
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        whats_on = mock_web_client()
        assert whats_on == mock_update

    def test_valid_request_web_client_2(self, mock_nexgen, mock_web_client):
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        whats_on = mock_web_client()
        assert whats_on == mock_update

    def test_normalized_keys(self, mock_david, mock_nexgen):
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)

        response_body_david = json.loads(mock_update_david['body'])
        response_body_nexgen = json.loads(mock_update_nexgen['body'])

        assert [*response_body_david['data']] == \
            [*response_body_nexgen['data']]

    def test_invalid_metadata_no_overwrite(self, mock_nexgen, mock_web_client):
        """
        Tests that providing invalid metadata does not result in valid
        data being overwritten.
        """
        resp_1 = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_nexgen('')
        resp_2 = mock_web_client()
        assert resp_1 == resp_2
