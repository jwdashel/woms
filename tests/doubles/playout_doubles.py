import pytest

from tests.test_data import playlist_hist

import whatsonms.php

@pytest.fixture
def patch_playlist_hist(monkeypatch):
    def stub_php(*arg, **kwargs):
        hist = playlist_hist()
        return next(hist)

    def stub_next_php(*args, **kwargs):
        hist = playlist_hist()
        next(hist)
        return next(hist)

    monkeypatch.setattr(whatsonms.php, "playlist_history_preview", stub_php)
    monkeypatch.setattr(whatsonms.php, "next_playlist_history_preview", stub_next_php)


