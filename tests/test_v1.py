from unittest.mock import call
from whatsonms import v1


def test_dict_vals_converted_encoding(mocker):
    mocker.patch('whatsonms.v1.utils.convert_encoding')
    v1.normalize_encodings({'call': 'me',
                            'may': 'be'})
    v1.utils.convert_encoding.assert_has_calls([call('me'), call('be')])
