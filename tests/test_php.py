import whatsonms.php as php
from unittest.mock import patch
import tests.test_data as test_data


class TestPlaylistHistoryPreview:
    @patch('whatsonms.php.metadb')
    def test_get_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = test_data.ddb_metadata()
        last_tunes = php.playlist_history_preview('wqxr')
        assert last_tunes[0]['soloist1'] == "Dustin Hoffman"
        assert last_tunes[1]['soloist1'] == "Ben Stiller"
        assert last_tunes[2]['soloist1'] == "Blythe Danner"
        assert len(last_tunes) == 3

    @patch('whatsonms.php.metadb')
    def test_update_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = test_data.ddb_metadata()
        last_tunes = php.next_playlist_history_preview('wqxr')
        assert last_tunes[0]['soloist1'] == "Barbra Streisand"
        assert last_tunes[1]['soloist1'] == "Dustin Hoffman"
        assert last_tunes[2]['soloist1'] == "Ben Stiller"
        assert len(last_tunes) == 3

    @patch('whatsonms.php.metadb')
    def test_no_php_get_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = test_data.ddb_metadata_no_hist()
        last_tunes = php.playlist_history_preview('wqxr')
        assert isinstance(last_tunes, list)
        assert len(last_tunes) == 0

    @patch('whatsonms.php.metadb')
    def test_no_php_update_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = test_data.ddb_metadata_no_hist()
        last_tunes = php.next_playlist_history_preview('wqxr')
        assert last_tunes[0]['soloist1'] == "Barbra Streisand"
        assert len(last_tunes) == 1

    @patch('whatsonms.php.metadb')
    def test_next_php_air_break(self, mock_metadb):
        mock_metadb.get_metadata.return_value = test_data.air_break_()
        last_tunes = php.next_playlist_history_preview('wqxr')
        assert last_tunes[0]['soloist1'] == "Dustin Hoffman"
        assert last_tunes[1]['soloist1'] == "Ben Stiller"
        assert last_tunes[2]['soloist1'] == "Blythe Danner"
        assert len(last_tunes) == 3
