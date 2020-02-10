import simplejson as json
import pytest
from urllib import parse
from datetime import datetime
from unittest.mock import MagicMock

from whatsonms.utils import Response
from whatsonms import v1
from whatsonms import php

DAVID_SAMPLE = './tests/david_archive_sample.xml'
DAVID_NO_PRESENT_TRACK = './tests/david_archive_sample__no_present_track.xml'
DAVID_NON_MUSIC_METADATA = './tests/david_non_music_metadata.xml'
DAVID_SPECIAL_CHARS = './tests/david_special_chars.xml'
DAVID_WEIRD_CDATA = './tests/david_weird_cdata.xml'
DAVID_NO_COMPOSER = './tests/david_no_composer.xml'
DAVID_NO_TITLE = './tests/david_no_title.xml'
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
NEXGEN_NODATE_XML = """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>I Concentrate On You</title>
<composer>Steve Lawrence</composer>
<number>978416</number>
</audio>
"""
NEXGEN_NOTITLE_XML = """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title></title>
<composer>Steve Lawrence</composer>
<number>978416</number>
</audio>
"""
NEXGEN_AIRBREAK_XML = """
<audio ID="id_2926362004_30792815">
<type>Alternate Text</type>
<status>Playing</status>
<number>0</number>
<length>00:00:00</length>
<played_time>00:00:00</played_time>
<title>WNYC2 New York Public Radio</title>
<artist></artist>
<composer></composer>
</audio>
"""
NEXGEN_SAMPLE_QS = parse.quote(NEXGEN_SAMPLE_XML, safe=())
NEXGEN_NODATE_QS = parse.quote(NEXGEN_NODATE_XML, safe=())
NEXGEN_NOTITLE_QS = parse.quote(NEXGEN_NOTITLE_XML, safe=())
NEXGEN_AIRBREAK_QS = parse.quote(NEXGEN_AIRBREAK_XML, safe=())


NORMALIZED_KEY_NAMES = [
    'album',
    'catno',
    'david_guid',
    'length',
    'mm_composer1',
    'mm_conductor',
    'mm_ensemble1',
    'mm_reclabel',
    'mm_soloist1',
    'mm_soloist2',
    'mm_soloist3',
    'mm_soloist4',
    'mm_soloist5',
    'mm_soloist6',
    'mm_uid',
    'start_time',
    'start_date',
    'title',
    'epoch_start_time',
    'playlist_hist_preview',
    'iso_start_time'
]


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
    def test_invalid_request_nexgen(self, qs_parameters, mock_nexgen, mock_next_php):
        resp = mock_nexgen(qs_parameters)
        assert resp['statusCode'] == 404

    @pytest.mark.parametrize('body', [{}])
    def test_invalid_request_david(self, body, mock_david, mock_next_php):
        resp = mock_david(body=body)
        assert resp['statusCode'] == 404

    def test_valid_request_nexgen(self, mocker, mock_nexgen, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']
        expected_response = '978416'
        assert metadata['mm_uid'] == expected_response

    def test_nexgen_has_php(self, mocker, mock_nexgen):
        playlist_history = ['aint', 'that', 'easy']
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mocker.patch('whatsonms.php.next_playlist_history_preview',
                     return_value=playlist_history)
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']
        assert 'playlist_hist_preview' in metadata
        php.next_playlist_history_preview.assert_called_once()
        assert metadata['playlist_hist_preview'] == playlist_history

    def test_no_date_nexgen(self, mocker, mock_nexgen, mock_next_php):
        # When NEXGEN sends XML without play date field
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mocker.patch('whatsonms.v1.datetime')

        expected_date = datetime(2018, 9, 13)
        expected_return_date = "09/13/2018"
        v1.datetime.today = MagicMock(return_value=expected_date)

        mock_update = mock_nexgen(NEXGEN_NODATE_QS)
        response_body = mock_update["body"]
        mock_update_body = self.clean_json_from_str(response_body)
        metadata = mock_update_body['data']['attributes']
        assert "start_date" in metadata

        v1.datetime.today.assert_called_once()
        assert metadata["start_date"] == expected_return_date

    def test_airbreak_nexgen(self, mocker, mock_nexgen, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))

        mock_update = mock_nexgen(NEXGEN_AIRBREAK_QS)
        response_body = mock_update["body"]
        mock_update_body = self.clean_json_from_str(response_body)
        metadata = mock_update_body['data']['attributes']['Item']['metadata']

        assert type(metadata['air_break']) is bool
        assert metadata['air_break']

    def test_valid_request_david(self, mocker, mock_david, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']
        expected_response = '126753'
        assert metadata['mm_uid'] == expected_response

    def test_david_has_php(self, mocker, mock_david):
        playlist_history = ['dr', 'funkenstein']
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mocker.patch('whatsonms.php.next_playlist_history_preview',
                     return_value=playlist_history)
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        metadata = mock_update_body['data']['attributes']
        assert 'playlist_hist_preview' in metadata
        php.next_playlist_history_preview.assert_called_once()
        assert metadata['playlist_hist_preview'] == playlist_history

    def test_air_break_response_from_david__no_present_track_element(self, mocker, mock_david,
                                                                     mock_web_client, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mocker.patch('whatsonms.php.playlist_history_preview', return_value=[])
        mock_david(sample_file=DAVID_NO_PRESENT_TRACK)
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes']['air_break'] is True

    def test_air_break_response_from_david__nonmusic_metadata(self, mocker, mock_david,
                                                              mock_web_client, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mocker.patch('whatsonms.php.playlist_history_preview', return_value=[])
        mock_david(sample_file=DAVID_NON_MUSIC_METADATA)
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes']['air_break'] is True

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
                                      mock_web_client, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_body = self.clean_json_from_str(mock_update['body'])
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes'] == \
            mock_update_body['data']['attributes']

    def test_valid_request_web_client_2(self, mocker, mock_nexgen, mock_next_php,
                                        mock_web_client):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_body = self.clean_json_from_str(mock_update['body'])

        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])

        assert whats_on_body['data']['attributes'] == \
            mock_update_body['data']['attributes']

    def test_normalize_david_keys(self, mocker, mock_david, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_david_body = self.clean_json_from_str(
            mock_update_david['body'])
        data_david = mock_update_david_body['data']['attributes']

        for k in [*data_david]:
            assert k in NORMALIZED_KEY_NAMES

    def test_normalize_nexgen_keys(self, mocker, mock_nexgen, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_nexgen_body = self.clean_json_from_str(
            mock_update_nexgen['body'])
        data_nexgen = mock_update_nexgen_body['data']['attributes']

        for k in [*data_nexgen]:
            assert k in NORMALIZED_KEY_NAMES

    def test_weird_david_cdata(self, mocker, mock_david,
                               mock_web_client, mock_php, mock_next_php):
        # sometimes (on the weekend) we get xml with double escaped CDATA
        # blocks. xmltodict chokes on these. gotta be able to handle it.
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_david(sample_file=DAVID_WEIRD_CDATA)
        whats_on = mock_web_client()
        whats_on_body = self.clean_json_from_str(whats_on['body'])
        assert whats_on_body['data']['attributes']['air_break'] is True

    def test_time_stamp_converted_to_unix_time_david(self, mocker, mock_david, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_david_body = self.clean_json_from_str(
            mock_update_david['body'])
        # ASSUME david Real_Start_Time = 2013-04-11 18:19:20.111
        assert mock_update_david_body['data']['attributes']['epoch_start_time'] \
            == 1365718760

    def test_time_stamp_converted_to_iso_time_david(self, mocker, mock_david, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_david = mock_david(sample_file=DAVID_SAMPLE)
        mock_update_david_body = self.clean_json_from_str(
            mock_update_david['body'])

        assert 'iso_start_time' in mock_update_david_body['data']['attributes']
        # ASSUME david Real_Start_Time = 2013-04-11 18:19:20.111
        assert mock_update_david_body['data']['attributes']['iso_start_time'] \
            == "2013-04-11T22:19:20+00:00"

    def test_composer_name_correctly_displayed(self, mocker, mock_david, mock_next_php):
        # So...
        # The composer/pianist Lucien-Léon-Guillaume Lambert is displaying as
        # Lucien-LÃ©on-Guillaume Lambert ... because that's how it comes from DAVID
        # Turns out publisher is using trusty windows-1252 encoding
        mock_update_david = mock_david(sample_file=DAVID_SPECIAL_CHARS)
        mock_update_david_body = self.clean_json_from_str(
            mock_update_david['body'])
        assert mock_update_david_body['data']['attributes']['mm_composer1'] == \
            'Lucien-Léon-Guillaume Lambert'

    def test_time_stamp_converted_to_unix_time_nexgen(self, mocker, mock_nexgen, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_nexgen_body = self.clean_json_from_str(
            mock_update_nexgen['body'])
        # ASSUME nexgen played_date = 11/06/2018
        #               played_time = 15:48:40
        assert mock_update_nexgen_body['data']['attributes']['epoch_start_time'] \
            == 1541537320

    def test_time_stamp_converted_to_iso_time_nexgen(self, mocker, mock_nexgen, mock_next_php):
        mocker.patch('whatsonms.utils.broadcast',
                     return_value=Response(200, message='mock response'))
        mock_update_nexgen = mock_nexgen(NEXGEN_SAMPLE_QS)
        mock_update_nexgen_body = self.clean_json_from_str(
            mock_update_nexgen['body'])
        # ASSUME nexgen played_date = 11/06/2018
        #               played_time = 15:48:40
        assert mock_update_nexgen_body['data']['attributes']['iso_start_time'] \
            == "2018-11-06T20:48:40+00:00"

    def test_invalid_metadata_no_overwrite(self, mocker, mock_nexgen, mock_next_php,
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

        assert resp_1_body['data']['attributes'] == \
            resp_2_body['data']['attributes']
