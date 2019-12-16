import whatsonms.php as php
from unittest.mock import patch

ddb_metadata = {
    "Item": {
        "metadata": {
            "iso_start_time": "2019-12-12t17:35:53+00:00",
            "start_time": "12:35:53",
            "epoch_start_time": "1576172153",
            "length": "00:03:25",
            "mm_soloist1": "barbra streisand",
            "mm_uid": "983817",
            "title": "if you were the only boy in the world",
            "start_date": "12/12/2019",
            "playlist_hist_preview": [
                {
                    "iso_start_time": "2019-12-12t16:35:53+00:00",
                    "start_time": "11:35:53",
                    "epoch_start_time": "1576172152",
                    "length": "00:03:25",
                    "mm_soloist1": "dustin hoffman",
                    "mm_uid": "983817",
                    "title": "if u were the second boy in the world",
                    "start_date": "12/12/2019",
                },
                {
                    "iso_start_time": "2019-12-12t15:35:53+00:00",
                    "start_time": "10:35:53",
                    "epoch_start_time": "1576172151",
                    "length": "00:03:25",
                    "mm_soloist1": "ben stiller",
                    "mm_uid": "983817",
                    "title": "if u were the third boy in the world",
                    "start_date": "12/12/2019",
                },
                {
                    "iso_start_time": "2019-12-12t14:35:53+00:00",
                    "start_time": "09:35:53",
                    "epoch_start_time": "1576172150",
                    "length": "00:03:25",
                    "mm_soloist1": "blythe danner",
                    "mm_uid": "983817",
                    "title": "if u were the only girl in the world",
                    "start_date": "12/12/2019",
                }
            ]
        }
    },
    "responsemetadata": {
        "retryattempts": 0
    }
}


class testplaylisthistorypreview:

    def setup_method(self):
        self.ddb_metadata = {
            "Item": {
                "metadata": {
                    "iso_start_time": "2019-12-12T17:35:53+00:00",
                    "start_time": "12:35:53",
                    "epoch_start_time": "1576172153",
                    "length": "00:03:25",
                    "mm_soloist1": "Barbra Streisand",
                    "mm_uid": "983817",
                    "title": "If You Were The Only Boy In The World",
                    "start_date": "12/12/2019",
                    "playlist_hist_preview": [
                        {
                            "iso_start_time": "2019-12-12T16:35:53+00:00",
                            "start_time": "11:35:53",
                            "epoch_start_time": "1576172152",
                            "length": "00:03:25",
                            "mm_soloist1": "Dustin Hoffman",
                            "mm_uid": "983817",
                            "title": "If u were the second boy in the world",
                            "start_date": "12/12/2019",
                        },
                        {
                            "iso_start_time": "2019-12-12T15:35:53+00:00",
                            "start_time": "10:35:53",
                            "epoch_start_time": "1576172151",
                            "length": "00:03:25",
                            "mm_soloist1": "Ben Stiller",
                            "mm_uid": "983817",
                            "title": "If u were the third boy in the world",
                            "start_date": "12/12/2019",
                        },
                        {
                            "iso_start_time": "2019-12-12T14:35:53+00:00",
                            "start_time": "09:35:53",
                            "epoch_start_time": "1576172150",
                            "length": "00:03:25",
                            "mm_soloist1": "Blythe Danner",
                            "mm_uid": "983817",
                            "title": "If u were the only girl in the world",
                            "start_date": "12/12/2019",
                        }
                    ]
                }
            },
            "ResponseMetadata": {
                "RetryAttempts": 0
            }
        }

        # In some cases (such as when this code is first deployed), there
        # will not be last played tracks in woms, so have to handle that
        # case.                                   -- jd 12\16\19
        self.ddb_metadata_no_hist = {
            "Item": {
                "metadata": {
                    "iso_start_time": "2019-12-12T17:35:53+00:00",
                    "start_time": "12:35:53",
                    "epoch_start_time": "1576172153",
                    "length": "00:03:25",
                    "mm_soloist1": "Barbra Streisand",
                    "mm_uid": "983817",
                    "title": "If You Were The Only Boy In The World",
                    "start_date": "12/12/2019",
                }
            },
            "ResponseMetadata": {
                "RetryAttempts": 0
            }
        }

    @patch('whatsonms.php.metadb')
    def test_get_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = self.ddb_metadata
        last_tunes = php.playlist_history_preview('wqxr')
        assert last_tunes[0]['mm_soloist1'] == "Dustin Hoffman"
        assert last_tunes[1]['mm_soloist1'] == "Ben Stiller"
        assert last_tunes[2]['mm_soloist1'] == "Blythe Danner"
        assert len(last_tunes) == 3

    @patch('whatsonms.php.metadb')
    def test_update_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = self.ddb_metadata
        last_tunes = php.next_playlist_history_preview('wqxr')
        assert last_tunes[0]['mm_soloist1'] == "Barbra Streisand"
        assert last_tunes[1]['mm_soloist1'] == "Dustin Hoffman"
        assert last_tunes[2]['mm_soloist1'] == "Ben Stiller"
        assert len(last_tunes) == 3

    @patch('whatsonms.php.metadb')
    def test_no_php_get_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = self.ddb_metadata_no_hist
        last_tunes = php.playlist_history_preview('wqxr')
        assert isinstance(last_tunes, list)
        assert len(last_tunes) == 0

    @patch('whatsonms.php.metadb')
    def test_no_php_update_php(self, mock_metadb):
        mock_metadb.get_metadata.return_value = self.ddb_metadata_no_hist
        last_tunes = php.next_playlist_history_preview('wqxr')
        assert last_tunes[0]['mm_soloist1'] == "Barbra Streisand"
        assert len(last_tunes) == 1

    @patch('whatsonms.php.metadb')
    def test_next_php_air_break(self, mock_metadb):
        pass
