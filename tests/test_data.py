from whatsonms.playout_systems import DAVID


def stream_name():
    return "mainstream"


def parsed_metadata():
    return {
        "catno": "25990",
        "david_guid": "{B8033E5E-4231-4C03-AE34-4FD23D4817DC}",
        "epoch_start_time": "1583789083",
        "iso_start_time": "2020-03-09T21:24:43+00:00",
        "length": "983377",
        "composer1": "FKA Twigs",
        "conductor": "Nicolas Jaar",
        "ensemble1": "Future",
        "reclabel": "Young Turks",
        "mm_uid": "110813",
        "start_time": "2020-03-09 17:24:43.000",
        "title": "holy terrain",
        "album": "MAGDALENE"
    }


def jsonapi_response():
    """
    sample response sent to the FE.
    NOTE: var names are dashed, not underscored
    """
    return {"data": {
        "type": "whats-on",
        "id": "whats-on",
        "attributes": {
            "air-break": False
        },
        "meta": {
            "source": DAVID
        },
        "relationships": {
            "current-track": {
                "data": {
                    "id": "mainstream_1583789083_110813",
                    "type": "track"
                    }
                },
            "recent-tracks": {
                "data": [
                    {
                        "id": "mainstream_1583264406_863483",
                        "type": "track"
                        },
                    {
                        "id": "mainstream_1583264407_239487",
                        "type": "track"
                        },
                    {
                        "id": "mainstream_1583264408_723409",
                        "type": "track"
                        }
                    ]
                }
            }
        },
        "included": [
            {
                "id": "mainstream_1583789083_110813",
                "type": "track",
                "attributes": {
                    "album": "MAGDALENE",
                    "catno": "25990",
                    "composer1": "FKA Twigs",
                    "conductor": "Nicolas Jaar",
                    "david-guid": "{B8033E5E-4231-4C03-AE34-4FD23D4817DC}",
                    "ensemble1": "Future",
                    "length": "983377",
                    "epoch-start-time": "1583789083",
                    "mm-uid": "110813",
                    "reclabel": "Young Turks",
                    "iso-start-time": "2020-03-09T21:24:43+00:00",
                    "start-time": "2020-03-09 17:24:43.000",
                    "title": "holy terrain"
                    }
                },
            {
                "id": "mainstream_1583264406_863483",
                "type": "track",
                "attributes": {
                    "album": "Pony",
                    "composer1": "Orville Peck",
                    "length": "123131",
                    "epoch-start-time": "1583264406",
                    "title": "Dead of Night",
                    "start-time": "2020-02-19T15:11:33+00:00",
                    "mm-uid": "863483"
                    }
                },
            {
                "id": "mainstream_1583264407_239487",
                "type": "track",
                "attributes": {
                    "album": "The Shape of Jazz to Come",
                    "composer1": "Ornette Coleman",
                    "length": "487493",
                    "epoch-start-time": "1583264407",
                    "mm-uid": "239487",
                    "start-time": "2020-02-19T15:03:12+00:00",
                    "title": "Eventually"
                    }
                },
            {
                "id": "mainstream_1583264408_723409",
                "type": "track",
                "attributes": {
                    "album": "Sometimes I Sit and Think, and Sometimes I Just Sit",
                    "composer1": "Courtney Barnett",
                    "length": "485935",
                    "epoch-start-time": "1583264408",
                    "mm-uid": "723409",
                    "start-time": "2020-02-19T14:51:58+00:00",
                    "title": "Pedestrian At Best",
                    }
                }
            ]
        }


# a well-formed, complete metadata entry
def ddb_response():
    return {
        "Item": {
            "metadata": {
                "iso_start_time": "2019-12-12T17:35:53+00:00",
                "start_time": "12:35:53",
                "epoch_start_time": "1576172153",
                "length": "00:03:25",
                "soloist1": "Barbra Streisand",
                "mm_uid": "983817",
                "title": "If You Were The Only Boy In The World",
                "start_date": "12/12/2019",
                "playlist_hist_preview": [
                    {
                        "iso_start_time": "2019-12-12T16:35:53+00:00",
                        "start_time": "11:35:53",
                        "epoch_start_time": "1576172152",
                        "length": "00:03:25",
                        "soloist1": "Dustin Hoffman",
                        "mm_uid": "983817",
                        "title": "If u were the second boy in the world",
                        "start_date": "12/12/2019",
                    },
                    {
                        "iso_start_time": "2019-12-12T15:35:53+00:00",
                        "start_time": "10:35:53",
                        "epoch_start_time": "1576172151",
                        "length": "00:03:25",
                        "soloist1": "Ben Stiller",
                        "mm_uid": "983817",
                        "title": "If u were the third boy in the world",
                        "start_date": "12/12/2019",
                    },
                    {
                        "iso_start_time": "2019-12-12T14:35:53+00:00",
                        "start_time": "09:35:53",
                        "epoch_start_time": "1576172150",
                        "length": "00:03:25",
                        "soloist1": "Blythe Danner",
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
        "soloist1": "Barbra Streisand",
        "mm_uid": "983817",
        "title": "If You Were The Only Boy In The World",
        "start_date": "12/12/2019",
        "playlist_hist_preview": [
            {
                "iso_start_time": "2019-12-12T16:35:53+00:00",
                "start_time": "11:35:53",
                "epoch_start_time": "1576172152",
                "length": "00:03:25",
                "soloist1": "Dustin Hoffman",
                "mm_uid": "983817",
                "title": "If u were the second boy in the world",
                "start_date": "12/12/2019",
            },
            {
                "iso_start_time": "2019-12-12T15:35:53+00:00",
                "start_time": "10:35:53",
                "epoch_start_time": "1576172151",
                "length": "00:03:25",
                "soloist1": "Ben Stiller",
                "mm_uid": "983817",
                "title": "If u were the third boy in the world",
                "start_date": "12/12/2019",
            },
            {
                "iso_start_time": "2019-12-12T14:35:53+00:00",
                "start_time": "09:35:53",
                "epoch_start_time": "1576172150",
                "length": "00:03:25",
                "soloist1": "Blythe Danner",
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
                "soloist1": "Dustin Hoffman",
                "mm_uid": "983817",
                "title": "If u were the second boy in the world",
                "start_date": "12/12/2019",
            },
            {
                "iso_start_time": "2019-12-12T15:35:53+00:00",
                "start_time": "10:35:53",
                "epoch_start_time": "1576172151",
                "length": "00:03:25",
                "soloist1": "Ben Stiller",
                "mm_uid": "983817",
                "title": "If u were the third boy in the world",
                "start_date": "12/12/2019",
            },
            {
                "iso_start_time": "2019-12-12t14:35:53+00:00",
                "start_time": "09:35:53",
                "epoch_start_time": "1576172150",
                "length": "00:03:25",
                "soloist1": "Blythe Danner",
                "mm_uid": "983817",
                "title": "if u were the only girl in the world",
                "start_date": "12/12/2019",
            }
        ]
    }


def playlist_hist():
    history = [
        {
            "album": "Pony",
            "mm_uid": "863483",
            "length": "123131",
            "epoch_start_time": "1583264406",
            "start_time": "2020-02-19T15:11:33+00:00",
            "composer1": "Orville Peck",
            "title": "Dead of Night"
        },
        {
            "album": "The Shape of Jazz to Come",
            "mm_uid": "239487",
            "epoch_start_time": "1583264407",
            "length": "487493",
            "start_time": "2020-02-19T15:03:12+00:00",
            "composer1": "Ornette Coleman",
            "title": "Eventually"
        },
        {
            "album": "Sometimes I Sit and Think, and Sometimes I Just Sit",
            "mm_uid": "723409",
            "epoch_start_time": "1583264408",
            "length": "485935",
            "start_time": "2020-02-19T14:51:58+00:00",
            "composer1": "Courtney Barnett",
            "title": "Pedestrian At Best"
        },
        {
            "album": "Baby on Baby",
            "mm_uid": "982343",
            "epoch_start_time": "1583264409",
            "composer1": "DaBaby",
            "title": "Suge"
        },
    ]
    start, stop = 0, 3
    while stop <= len(history):
        yield history[start:stop]
        start += 1
        stop += 1


# metadata with no playlist history
def ddb_metadata_no_hist():
    # In some cases (such as a new stream), there will not be last played tracks in
    # woms, so have to handle that case.                             -- jd 12\16\19
    return {
        "iso_start_time": "2019-12-12T17:35:53+00:00",
        "start_time": "12:35:53",
        "epoch_start_time": "1576172153",
        "length": "00:03:25",
        "soloist1": "Barbra Streisand",
        "mm_uid": "983817",
        "title": "If You Were The Only Boy In The World",
        "start_date": "12/12/2019",
    }


def nexgen_sample():
    return nexgen_sample_0()


def nexgen_sample_0():
    return """
<audio ID="id-3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_date>11/06/2018</played_date>
<played_time>16:48:40</played_time>
<length>00:03:31</length>
<title>Ruby, My Dear</title>
<album_title>Monk's Music</album_title>
<comment1>Thelonius Monk</comment1>
<alt_artist>Thelonius Monk Septet</alt_artist>
<composer>Coleman Hawkins</composer>
<licensor>Monk</licensor>
<number>101017</number>
</audio>
"""


def nexgen_sample_1():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_date>11/06/2018</played_date>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>Groovallegiance</title>
<album_title>One Nation Under a Groove</album_title>
<composer>George Clinton</composer>
<alt_artist>P-Funk</alt_artist>
<licensor>Bootsy Collins</licensor>
<comment1>Funkadelic</comment1>
<number>978416</number>
</audio>
"""


def nexgen_nodate():
    return """
<audio ID="id_3189206699_30701071">
<type>Song</type>
<status>None</status>
<played_time>15:48:40</played_time>
<length>00:03:31</length>
<title>Bank Account</title>
<composer>21 Savage</composer>
<alt_artist>Metro Boomin</alt_artist>
<licensor>21 Savage</licensor>
<album_title>Issa Album</album_title>
<comment1>21 Savage</comment1>
<number>978416</number>
</audio>
"""


def nexgen_airbreak():
    # `title` is the key field here
    # its contents indicate air break
    return """
<audio ID="id_2926362004_30792815">
<type>Alternate Text</type>
<status>Playing</status>
<number>0</number>
<length>00:00:00</length>
<played_time>00:00:00</played_time>
<title>WNYC2 New York Public Radio</title>
<artist></artist>
<composer></composer>
</audio>
"""


def david_sample(ver=0):
    '''
    Gives a DAViD update body.
    Args:
        ver: david samples with different content (currently supporting [0..1])
    '''
    with open(f'tests/david_exports/david_sample_{ver}.xml') as f:
        return f.read()


def david_airbreak():
    with open('tests/david_exports/david_non_music_metadata.xml') as f:
        return f.read()
