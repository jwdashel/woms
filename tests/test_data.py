# a well-formed, complete metadata entry
def ddb_response():
    return {
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


# a well-formed, complete metadata entry
def ddb_metadata():
    return {
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


# metadata for when there is nothing on air (ad or host spot)
def air_break_():
    return {
        "air_break": True,
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


# metadata with no playlist history
def ddb_metadata_no_hist():
    # In some cases (such as a new stream), there will not be last played tracks in
    # woms, so have to handle that case.                             -- jd 12\16\19
    return {
        "iso_start_time": "2019-12-12T17:35:53+00:00",
        "start_time": "12:35:53",
        "epoch_start_time": "1576172153",
        "length": "00:03:25",
        "mm_soloist1": "Barbra Streisand",
        "mm_uid": "983817",
        "title": "If You Were The Only Boy In The World",
        "start_date": "12/12/2019",
    }
