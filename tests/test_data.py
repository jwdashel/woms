def stream_name():
    return "mainstream"

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

def playlist_hist():
    history = [
        {
            "album": "Pony",
            "mm_uid": "863483",
            "epoch_start_time": "1583264406",
            "mm_composer": "Orville Peck",
            "title": "Dead of Night"
        },
        {
            "album": "The Shape of Jazz to Come",
            "mm_uid": "239487",
            "epoch_start_time": "1583264407",
            "mm_composer": "Ornette Coleman",
            "title": "Eventually"
        },
        {
            "album": "Sometimes I Sit and Think, and Sometimes I Just Sit",
            "mm_uid": "723409",
            "epoch_start_time": "1583264408",
            "mm_composer": "Courtney Barnett",
            "title": "Pedestrian At Best"
        },
        {
            "album": "Baby on Baby",
            "mm_uid": "982343",
            "epoch_start_time": "1583264409",
            "mm_composer": "DaBaby",
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
        "mm_soloist1": "Barbra Streisand",
        "mm_uid": "983817",
        "title": "If You Were The Only Boy In The World",
        "start_date": "12/12/2019",
    }


def nexgen_sample():
    return nexgen_sample_0()


def nexgen_sample_0():
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


def nexgen_sample_1():
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
    with open(f'tests/david_xmls/david_sample_{ver}.xml') as f:
        return f.read()


def david_airbreak():
    with open('tests/david_non_music_metadata.xml') as f:
        return f.read()

def parsed_metadata():
    # Metadata freshly parsed from david or nexgen
    return {
        "album": "1000 gecs",
        "length": "10",
        "mm_composer1": "100 gecs",
        "title": "stupid horse",
        "mm_uid": "10000",
        "epoch_start_time": 1582755110
    }

def playlist_hist_preview():
    return [
        {
            "album": "lost time",
            "length": "873",
            "mm_composer1": "tacocat",
            "title": "i hate the weekend",
            "mm_uid": "98122",
            "epoch_start_time": 1582755111
        },
        {
            "album": "speak no evil",
            "length": "912",
            "mm_composer1": "wayne shorter",
            "title": "witch hunt",
            "mm_uid": "1966",
            "epoch_start_time": 1582755112
        },
        {
            "album": "hounds of love",
            "length": "123",
            "mm_composer1": "kate bush",
            "title": "running up that hill",
            "mm_uid": "1985",
            "epoch_start_time": 1582755113
        }
    ]

def jsonapi_response():
     return {
        "data": {
            "type": "whats-on",
            "id": "whats-on",
            "attributes": {
                "air-break": False
            },
            "meta": {
                "source": "DAViD"
            },
            "relationships": {
                "track": {
                    "data": {
                        "id": f"{stream_name()}_1582755110_10000",
                        "type": "track"
                    }
                },
                "recent-tracks": {
                    "data": [
                        {
                            "id": f"{stream_name()}_1582755111_98122",
                            "type": "track"
                        },
                        {
                            "id": f"{stream_name()}_1582755112_1966",
                            "type": "track"
                        },
                        {
                            "id": f"{stream_name()}_1582755113_1985",
                            "type": "track"
                        }
                    ]
                }
            }
        },
        "included": [
            {
                "id": f"{stream_name()}_1582755110_10000",
                "type": "track",
                "attributes": 
                {
                    "album": "1000 gecs",
                    "length": "10",
                    "mm_composer1": "100 gecs",
                    "title": "stupid horse",
                    "mm_uid": "10000",
                    "epoch_start_time": 1582755110
                }
            },
            {
                "id": f"{stream_name()}_1582755111_98122",
                "type": "track",
                "attributes": 
                {
                    "album": "lost time",
                    "length": "873",
                    "mm_composer1": "tacocat",
                    "title": "i hate the weekend",
                    "mm_uid": "98122",
                    "epoch_start_time": 1582755111
                }
            },
            {
                "id": f"{stream_name()}_1582755112_1966",
                "type": "track",
                "attributes": 
                {
                    "album": "speak no evil",
                    "length": "912",
                    "mm_composer1": "wayne shorter",
                    "title": "witch hunt",
                    "mm_uid": "1966",
                    "epoch_start_time": 1582755112
                }
            },
            {
                "id": f"{stream_name()}_1582755113_1985",
                "type": "track",
                "attributes": 
                {
                    "album": "hounds of love",
                    "length": "123",
                    "mm_composer1": "kate bush",
                    "title": "running up that hill",
                    "mm_uid": "1985",
                    "epoch_start_time": 1582755113
                }
            }
        ]
    }

