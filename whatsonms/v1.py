import logging
from typing import Dict
from datetime import datetime

import whatsonms.utils as utils

import xmltodict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


DAVID_MUSIC_ELEMS = (
    ('Music_Album', 'album'),
    ('Music_CDID', 'catno'),
    ('GUID', 'david_guid'),
    ('Time_Duration', 'length'),
    ('Music_Composer', 'mm_composer1'),
    ('USA.WNYC.CONDUCTOR', 'mm_conductor'),
    ('USA.WNYC.ORCHESTRA', 'mm_ensemble1'),
    ('CDINFO.LABEL', 'mm_reclabel'),
    ('USA.WNYC.SOLOIST1', 'mm_soloist1'),
    ('USA.WNYC.SOLOIST2', 'mm_soloist2'),
    ('USA.WNYC.SOLOIST3', 'mm_soloist3'),
    ('USA.WNYC.SOLOIST4', 'mm_soloist4'),
    ('USA.WNYC.SOLOIST5', 'mm_soloist5'),
    ('USA.WNYC.SOLOIST6', 'mm_soloist6'),
    ('Music_MusicID', 'mm_uid'),
    ('Time_RealStart', 'real_start_time'),
    ('', 'start_date'),
    ('Time_Start', 'start_time'),
    ('Title', 'title'),
)

NEXGEN_MUSIC_ELEMS = (
    ('album_title', 'album'),
    ('', 'catno'),
    ('', 'david_guid'),
    ('length', 'length'),
    ('comment1', 'mm_composer1'),
    ('', 'mm_conductor'),
    ('alt_artist', 'mm_ensemble1'),
    ('', 'mm_reclabel'),
    ('composer', 'mm_soloist1'),
    ('licensor', 'mm_soloist2'),
    ('', 'mm_soloist3'),
    ('', 'mm_soloist4'),
    ('', 'mm_soloist5'),
    ('', 'mm_soloist6'),
    ('number', 'mm_uid'),
    ('', 'real_start_time'),
    ('played_date', 'start_date'),
    ('played_time', 'start_time'),
    ('title', 'title'),
)


def air_break() -> dict:
    return {"air_break": True}


def normalize_david_dict(present_track_info: dict) -> dict:
    normalized = {v: present_track_info.get(k) for k, v in DAVID_MUSIC_ELEMS if k in present_track_info}
    return normalized


def standardize_timestamps(track_info):
    if 'start_date' in track_info:
        # NEXGEN
        track_info['epoch_start_time'] = utils.convert_date_time(track_info['start_date'], track_info['start_time'])
    else:
        # DAVID
        track_info['epoch_start_time'] = utils.convert_time(track_info['start_time'])

    track_info['iso_start_time'] = utils.convert_time_to_iso(track_info['epoch_start_time'])

    if 'real_start_time' in track_info:
        track_info['epoch_real_start_time'] = utils.convert_time(track_info['real_start_time'])
        track_info['iso_real_start_time'] = utils.convert_time_to_iso(track_info['epoch_real_start_time'])

    return track_info


def normalize_encodings(present_track_info: dict) -> dict:
    for key in present_track_info.keys():
        if present_track_info[key]:
            present_track_info[key] = utils.convert_encoding(present_track_info[key])
    return present_track_info


def parse_metadata_nexgen(event: Dict) -> Dict:
    """
    Parse new metadata from NexGen -- format it as JSON and return it.
    """
    xml = event.get('queryStringParameters', {}).get('xml_contents')
    if xml:
        xmldict = xmltodict.parse(xml)
        normalized = {
            v: xmldict['audio'].get(k) for k, v in NEXGEN_MUSIC_ELEMS if k in xmldict['audio']
        }
        if "start_date" not in normalized:
            normalized["start_date"] = datetime.today().strftime('%m/%d/%Y')

        normalized = standardize_timestamps(normalized)

        return normalized


def parse_metadata_david(event: Dict) -> Dict:
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
                return air_break()
            present = normalize_encodings(present)
            present = normalize_david_dict(present)
            present = standardize_timestamps(present)
            return present
        except ValueError:
            # ValueError thrown if no 'present' track in xmldict
            return air_break()
