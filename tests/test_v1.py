from unittest.mock import call, patch
from whatsonms import v1
from whatsonms.playout_systems import DAVID
import tests.test_data as test_data


def test_dict_vals_converted_encoding(mocker):
    mocker.patch('whatsonms.v1.utils.convert_encoding')
    v1.normalize_encodings({'call': 'me',
                            'may': 'be'})
    v1.utils.convert_encoding.assert_has_calls([call('me'), call('be')])


@patch('whatsonms.php.metadb')
def test_air_break_includes_php(mock_metadb):
    mock_metadb.get_metadata.return_value = test_data.ddb_metadata()
    response = v1.air_break('wqxr', DAVID)
    assert len(response['data']['relationships']['recent-tracks']['data']) == 3
