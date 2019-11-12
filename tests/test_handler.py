import simplejson as json
import pytest
from urllib import parse

from whatsonms.utils import Response

DAVID_SAMPLE = './tests/david_archive_sample.xml'
DAVID_NO_PRESENT_TRACK = './tests/david_archive_sample__no_present_track.xml'
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
    def clean_json_from_str(self, json_str: str):
        """
        Cleans up the escaped-single-quote json that AWS produces.
        Args:
            json_str: A string containing the single-quote syntax
        Returns: A tidy double-quoted json dict
        """
        json_str = json_str.replace("\'{\"", "{\"")
        json_str = json_str.replace("\"}\'", "\"}")
        json_str = json_str.replace("\'", "'")
        return json.loads(json_str)

    @pytest.mark.parametrize('qs_parameters', [''])
    def test_invalid_request_nexgen(self, qs_parameters, mock_nexgen):
        resp = mock_nexgen(qs_parameters)
        assert resp['statusCode'] == 404

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body, mock_david):
        resp = mock_david(body=body)
        assert resp['statusCode'] == 404

    def test_valid_request_nexgen(self, mocker, mock_nexgen):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']['Item']['metadata']
        expected_response = '978416'
        assert metadata['mm_uid'] == expected_response

    def test_valid_request_david(self, mocker, mock_david):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']['Item']['metadata']
        expected_response = '126753'
        assert metadata['mm_uid'] == expected_response

    def test_response_from_david__no_present_track_element(self, mocker, mock_david,
                                                           mock_web_client):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_david(sample_file=DAVID_NO_PRESENT_TRACK)
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes']['Item']['metadata']['air_break'] is True

    def test_invalid_request_web_client(self, mock_web_client):
        resp = mock_web_client(stream_slug='foobar')
        resp_body = self.clean_json_from_str(resp['body'])
        metadata = resp_body['data'].get('metadata', None)
        # assert resp['statusCode'] == 404
        #
        # TODO: figure out why mock_dynamodb2 is sending back a different
        # response than real dynamodb does from db.get_metadata. This
        # tricks http.get() into thinking there is metadata and sends
        # back a 200 Response, when actually there isn't metadata in the
        # resp_body. Ideally we would assert the statusCode is 404, not
        # that metadata is None.
        assert metadata is None

    def test_valid_request_web_client(self, mocker, mock_david,
                                      mock_web_client):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes']['Item'] == \
            mock_update_body['data']['attributes']['Item']

    def test_valid_request_web_client_2(self, mocker, mock_nexgen,
                                        mock_web_client):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_body = self.clean_json_from_str(mock_update['body'])

        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])

        assert whats_on_body['data']['attributes']['Item'] == \
            mock_update_body['data']['attributes']['Item']

    def test_normalized_keys(self, mocker, mock_david, mock_nexgen):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_david_body = self.clean_json_from_str(mock_update_david['body'])
        data_david = mock_update_david_body['data']['attributes']['Item']

        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_nexgen_body = self.clean_json_from_str(mock_update_nexgen['body'])
        data_nexgen = mock_update_nexgen_body['data']['attributes']['Item']

        assert [*data_david] == [*data_nexgen]

    def test_time_stamp_converted_to_unix_time_david(self, mocker, mock_david):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_david_body = self.clean_json_from_str(mock_update_david['body'])
        # ASSUME david Start_Time = 2013-04-11 18:19:07.986
        assert mock_update_david_body['data']['attributes']['Item']['metadata']['epoch_start_time'] \
            == 1365718747
        # ASSUME david Real_Start_Time = 2013-04-11 18:19:20.111
        assert mock_update_david_body['data']['attributes']['Item']['metadata']['epoch_real_start_time'] \
            == 1365718760

    def test_time_stamp_converted_to_unix_time_nexgen(self, mocker, mock_nexgen):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_nexgen_body = self.clean_json_from_str(mock_update_nexgen['body'])
        # ASSUME nexgen played_date = 11/06/2018
        #               played_time = 15:48:40
        assert mock_update_nexgen_body['data']['attributes']['Item']['metadata']['epoch_start_time'] \
            == 1541537320

    def test_invalid_metadata_no_overwrite(self, mocker, mock_nexgen,
                                           mock_web_client):
        """
        Tests that providing invalid metadata does not result in valid
        data being overwritten.
        """
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        resp_1 = mock_nexgen(NEXGEN_SAMPLE_QS)
        resp_1_body = self.clean_json_from_str(resp_1['body'])

        mock_nexgen('')
        resp_2 = mock_web_client()
        resp_2_body = self.clean_json_from_str(resp_2['body'])

        assert resp_1_body['data']['attributes']['Item'] == \
            resp_2_body['data']['attributes']['Item']
