import pytest
from moto import mock_dynamodb2

import tests.test_data as test_data
from whatsonms.config import TABLE_METADATA, TABLE_SUBSCRIBERS

from whatsonms.response import Response

import whatsonms.php


@pytest.fixture
def patch_playlist_hist(monkeypatch):
    def stub_php(*arg, **kwargs):
        hist = test_data.playlist_hist()
        return next(hist)

    def stub_next_php(*args, **kwargs):
        hist = test_data.playlist_hist()
        next(hist)
        return next(hist)

    monkeypatch.setattr(whatsonms.php, "playlist_history_preview", stub_php)
    monkeypatch.setattr(whatsonms.php, "next_playlist_history_preview", stub_next_php)


@pytest.fixture
def mock_thin_ddb():
    """
    Enables ddb fakes but does not instantiate fake tables.
    """
    with mock_dynamodb2():
        yield


@pytest.fixture
def mock_dynamodb_tables():
    """
    Enables ddb fakes and sets up fakes for the DDB tables WOMs uses.
    """
    with mock_dynamodb2():
        from whatsonms.dynamodb import MetadataDB, SubscriberDB
        MetadataDB(TABLE_METADATA)
        SubscriberDB(TABLE_SUBSCRIBERS)
        yield


@pytest.fixture
def patch_broadcast(mocker):
    history = test_data.playlist_hist()
    mocker.patch('whatsonms.response.broadcast', return_value=Response(test_data.parsed_metadata(),
                 next(history), test_data.stream_name(), ""))
