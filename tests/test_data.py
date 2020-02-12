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


def nexgen_sample():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_date>11/06/2018</played_date>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>One Nation Under a Groove</title>
<comment1>Funkadelic</comment1>
<number>978416</number>
</audio>
"""


def nexgen_sample_2():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_date>11/06/2018</played_date>
<played_time>16:48:40</played_time>
<length>00:03:31</length>
<title>Ruby, My Dear</title>
<comment1>Thelonius Monk</comment1>
<number>101017</number>
</audio>
"""


def nexgen_nodate():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>One Nation Under a Groove</title>
<composer>Funkadelic</composer>
<number>978416</number>
</audio>
"""


def nexgen_notitle():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title></title>
<composer>Funkadelic</composer>
<number>978416</number>
</audio>
"""


def david_sample(ver=0):
    '''
    Gives a DAViD update body.
    Args:
        ver: david samples with different content (currently supporting [0..0])
    '''
    with open(f'tests/david_xmls/david_sample_{ver}.xml') as f:
        return f.read()
