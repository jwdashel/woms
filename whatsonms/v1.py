import logging
from typing import Dict
from datetime import datetime

import whatsonms.utils as utils
import whatsonms.php as php
from whatsonms.response import Response
from whatsonms.playout_systems import DAVID, NEXGEN

import xmltodict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


DAVID_MUSIC_ELEMS = (
    ('Music_Album', 'album'),
    ('Music_CDID', 'catno'),
    ('GUID', 'david_guid'),
    ('Time_Duration', 'length'),
    ('Music_Composer', 'composer'),
    ('USA.WNYC.CONDUCTOR', 'conductor'),
    ('USA.WNYC.ORCHESTRA', 'ensemble'),
    ('CDINFO.LABEL', 'reclabel'),
    ('USA.WNYC.SOLOIST1', 'soloist1'),
    ('USA.WNYC.SOLOIST2', 'soloist2'),
    ('USA.WNYC.SOLOIST3', 'soloist3'),
    ('USA.WNYC.SOLOIST4', 'soloist4'),
    ('USA.WNYC.SOLOIST5', 'soloist5'),
    ('USA.WNYC.SOLOIST6', 'soloist6'),
    ('Music_MusicID', 'mm_uid'),
    # MAP DAVID's Time_RealStart to start_time
    # Front end consumes `start_time`
    # Populate `start_time` with `Time_RealStart` for accurate
    # representation of when track starts (DSODA-315) -- ss
    ('Time_RealStart', 'start_time'),
    # ('Time_Start', 'start_time'),
    ('', 'start_date'),
    ('Title', 'title'),
)

NEXGEN_MUSIC_ELEMS = (
    ('album_title', 'album'),
    ('', 'catno'),
    ('', 'david_guid'),
    ('length', 'length'),
    ('comment1', 'composer'),
    ('', 'conductor'),
    ('alt_artist', 'ensemble'),
    ('', 'reclabel'),
    ('composer', 'soloist1'),
    ('licensor', 'soloist2'),
    ('', 'soloist3'),
    ('', 'soloist4'),
    ('', 'soloist5'),
    ('', 'soloist6'),
    ('number', 'mm_uid'),
    ('', 'real_start_time'),
    ('played_date', 'start_date'),
    ('played_time', 'start_time'),
    ('title', 'title'),
)


class DavidDataException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NexgenDataException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def air_break(stream: str, playout_sys: str) -> dict:
    playlist_hist = php.playlist_history_preview(stream)
    return Response(None, playlist_hist, stream, playout_sys)


def normalize_david_dict(present_track_info: dict) -> dict:
    normalized = {v: present_track_info.get(k, None) for k, v in DAVID_MUSIC_ELEMS}
    normalized['playout_system'] = DAVID
    return normalized


def standardize_timestamps(track_info: dict) -> dict:
    if track_info['playout_system'] == NEXGEN:
        track_info['epoch_start_time'] = utils.convert_date_time(track_info['start_date'], track_info['start_time'])
        del track_info['start_date']
        del track_info['start_time']
    elif track_info['playout_system'] == DAVID:
        track_info['epoch_start_time'] = utils.convert_time(track_info['start_time'])
        del track_info['start_time']

    track_info['start_time'] = utils.convert_time_to_iso(track_info['epoch_start_time'])

    return track_info


def normalize_encodings(present_track_info: dict) -> dict:
    for key in present_track_info.keys():
        if present_track_info[key]:
            present_track_info[key] = utils.convert_encoding(present_track_info[key])
    return present_track_info


def collapse_soloists(present_track_info: dict) -> dict:
    """
    DAVID can provide up to 6 soloists and NEXGEN can provide up to two.
    They are parsed as soloist1 .. soloist6 (or soloist2 for NG).
    This squishes them down into one array element for a cleaner client
    experience.
    There is probably a way to do this a _bit_ more cleanly than this
    implementation, but I am going with the Law of Good Enuff here.
    """
    soloists = [f'soloist{number}' for number in range(1, 7)]
    present_track_info['soloists'] = []
    for soloist in soloists:
        if present_track_info[soloist]:
            present_track_info['soloists'].append(present_track_info[soloist])
        del present_track_info[soloist]
    return present_track_info


def parse_metadata_nexgen(event: Dict, stream) -> Dict:
    """
    Parse new metadata from NexGen -- format it as JSON and return it.
    """
    xml = event.get('queryStringParameters', {}).get('xml_contents')
    if xml:
        xmldict = xmltodict.parse(xml)
        normalized = {v: xmldict['audio'].get(k, None) for k, v in NEXGEN_MUSIC_ELEMS}
        normalized['playout_system'] = NEXGEN

        if not normalized["start_date"]:
            normalized["start_date"] = datetime.today().strftime('%m/%d/%Y')

        if int(normalized["mm_uid"]) == 0:
            return None

        normalized = standardize_timestamps(normalized)
        collapse_soloists(normalized)

        return normalized


def parse_metadata_david(event: Dict, stream) -> Dict:
    """
    Parse new metadata from DAVID -- format it as JSON and return it.
    """
    xml = event.get('body')
    if xml:
        xml = utils.sanitize_cdata(xml)
        xmldict = xmltodict.parse(xml)
        try:
            present, = (x for x in xmldict['wddxPacket']['item']
                        if x['@sequence'] == 'present')

            if present['Class'] != "Music":
                return None

            present = normalize_david_dict(present)
            normalize_encodings(present)
            standardize_timestamps(present)
            collapse_soloists(present)

            return present
        except ValueError:
            # ValueError thrown if no 'present' track in xmldict
            return None
