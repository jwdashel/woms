import pytest
from urllib import parse
from datetime import datetime
from unittest.mock import MagicMock

import whatsonms.handler

from whatsonms.playout_systems import DAVID, NEXGEN
from whatsonms.config import URL_PREFIX
from whatsonms import v1

import tests.test_data as test_data

WQXR_STREAM_SLUG = 'wqxr'

DAVID_SAMPLE = pytest.param('./tests/david_exports/david_export_sample.xml', id='DAVID_SAMPLE')
DAVID_NON_MUSIC_METADATA = pytest.param('./tests/david_exports/david_non_music_metadata.xml', id='DAVID_NON_MUSIC_METADATA')
DAVID_NO_PRESENT_TRACK = pytest.param('./tests/david_exports/david_no_present_track.xml', id='DAVID_NO_PRESENT_TRACK')
DAVID_SPECIAL_CHARS = pytest.param('./tests/david_exports/david_special_chars.xml', id='DAVID_SPECIAL_CHARS')

DAVID_SAMPLE_XML = './tests/david_exports/david_export_sample.xml'
DAVID_SPECIAL_CHARS_XML = './tests/david_exports/david_special_chars.xml'

# sometimes (on the weekend) we get xml with double escaped CDATA
# blocks. xmltodict chokes on these. gotta be able to handle it.
DAVID_WEIRD_CDATA = pytest.param('./tests/david_exports/david_weird_cdata.xml', id='DAVID_WEIRD_CDATA')

NEXGEN_SAMPLE = pytest.param(parse.quote(test_data.nexgen_sample(), safe=()), id='NEXGEN_SAMPLE')
NEXGEN_NODATE = pytest.param(parse.quote(test_data.nexgen_nodate(), safe=()), id='NEXGEN_NODATE')
NEXGEN_AIRBREAK = pytest.param(parse.quote(test_data.nexgen_airbreak(), safe=()), id='NEXGEN_AIRBREAK')

NEXGEN_SAMPLE_QS = parse.quote(test_data.nexgen_sample(), safe=())


class TestPlayout:
    def lambda_maker(self, content):
        if self.playout_system == DAVID:
            with open(content, 'rb') as body:
                body = body.read().decode('utf8')
                return {
                    'body': body,
                    'httpMethod': 'POST',
                    'path': URL_PREFIX + '/v1/update',
                    'queryStringParameters': {
                        'stream': test_data.stream_name()
                    },
                }
        elif self.playout_system == NEXGEN:
            xml_contents = parse.unquote(content)
            return {
                'httpMethod': 'GET',
                'path': URL_PREFIX + '/v1/update',
                'queryStringParameters': {
                    'stream': test_data.stream_name(),
                    'xml_contents': xml_contents
                },
            }

    def validate_whatson(self, whatson_response):
        for item in whatson_response['included']:
            for field in self.metadata_fields:
                assert field in item['attributes']
                assert item['attributes'][field] is not None

    def php_test(self):
        # php will collect last tracks as they play
        for i in range(1, 5):
            lambda_invocation = self.lambda_maker(self.generic_test_data)
            whatson_response = whatsonms.handler(lambda_invocation, {})
            assert len(whatson_response['included']) == i

        # php will never have more than 3 tracks
        # so including whats on now, there will never be more than 4 tracks
        for i in range(5, 10):
            lambda_invocation = self.lambda_maker(self.generic_test_data)
            whatson_response = whatsonms.handler(lambda_invocation, {})
            assert len(whatson_response['included']) == 4


class TestDavidPlayout(TestPlayout):
    """
    Tests for how WOMs will handle the outputs delivered from DAViD playouts.
    """
    playout_system = DAVID
    generic_test_data = DAVID_SAMPLE_XML
    # these metadata fields use dashes bc that's how the Frontend wants it
    metadata_fields = ['album', 'catno', 'david-guid', 'epoch-start-time', 'iso-start-time',
                       'length', 'composer1', 'conductor', 'ensemble1', 'reclabel',
                       'mm-uid', 'start-time', 'title']

    @pytest.mark.parametrize('david_sample', [DAVID_SAMPLE, DAVID_SPECIAL_CHARS])
    def test_david_playout(self, david_sample, patch_broadcast, mock_dynamodb_tables):
        lambda_invocation = self.lambda_maker(david_sample)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        self.validate_whatson(whatson_response)
        assert not whatson_response['data']['attributes']['air-break']

    @pytest.mark.parametrize('david_airbreak_sample', [DAVID_NON_MUSIC_METADATA,
                                                       DAVID_WEIRD_CDATA,
                                                       DAVID_NO_PRESENT_TRACK])
    def test_david_airbreak(self, david_airbreak_sample, patch_broadcast, mock_dynamodb_tables):
        lambda_invocation = self.lambda_maker(david_airbreak_sample)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        self.validate_whatson(whatson_response)

        assert whatson_response['data']['attributes']['air-break']

    def test_david_handles_special_chars(self, patch_broadcast, mock_dynamodb_tables):
        lambda_invocation = self.lambda_maker(DAVID_SPECIAL_CHARS_XML)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        assert whatson_response['included'][0]['attributes']['composer1'] == \
            'Lucien-Léon-Guillaume Lambert'

    def test_php(self, patch_broadcast, mock_dynamodb_tables):
        self.php_test()


class TestNexGenPlayout(TestPlayout):
    """
    Tests for how WOMs will handle the outputs delivered from NexGen playouts.
    """
    playout_system = NEXGEN
    generic_test_data = NEXGEN_SAMPLE_QS
    # these metadata fields use dashes bc that's how the Frontend wants it
    metadata_fields = ['album', 'length', 'composer1', 'ensemble1',
                       'soloist1', 'soloist2', 'mm-uid', 'start-date',
                       'start-time', 'title']

    @pytest.mark.parametrize('nexgen_input', [NEXGEN_SAMPLE, NEXGEN_NODATE])
    def test_nexgen(self, nexgen_input, patch_broadcast, mock_dynamodb_tables):
        lambda_invocation = self.lambda_maker(nexgen_input)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        self.validate_whatson(whatson_response)

    @pytest.mark.parametrize('nexgen_input', [NEXGEN_AIRBREAK])
    def test_nexgen_airbreak(self, nexgen_input, patch_broadcast, mock_dynamodb_tables):
        lambda_invocation = self.lambda_maker(nexgen_input)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        assert whatson_response['data']['attributes']['air-break']

    def test_php(self, patch_broadcast, mock_dynamodb_tables):
        self.php_test()

    @pytest.mark.parametrize('nexgen_input', [NEXGEN_NODATE])
    def test_nodate_xml(self, nexgen_input, mocker, patch_broadcast, mock_dynamodb_tables):
        """
        Sometimes nexgen sends an update with no date in the xml. Let's make sure woms adds one.
        """
        mocker.patch('whatsonms.v1.datetime')
        expected_date = datetime(2018, 9, 13)
        expected_return_date = "09/13/2018"
        v1.datetime.today = MagicMock(return_value=expected_date)

        lambda_invocation = self.lambda_maker(nexgen_input)
        whatson_response = whatsonms.handler(lambda_invocation, {})

        v1.datetime.today.assert_called_once()
        assert whatson_response['included'][0]['attributes']['start-date'] == expected_return_date
