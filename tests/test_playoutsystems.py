import whatsonms.php as php


def test_php(patch_playlist_hist):
    print(php.playlist_history_preview())
    print(php.next_playlist_history_preview())
    assert True
