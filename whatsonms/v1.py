import logging
from typing import Dict

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


def parse_metadata_nexgen(event: Dict) -> Dict:
    """
    Parse new metadata from NexGen -- format it as JSON and return it.
    """
    xml = event.get('queryStringParameters', {}).get('xml_contents')
    if xml:
        xmldict = xmltodict.parse(xml)
        normalized = {
            v: xmldict['audio'].get(k, '') for k, v in NEXGEN_MUSIC_ELEMS
        }
        return normalized


def parse_metadata_david(event: Dict) -> Dict:
    """
    Parse new metadata from DAVID -- format it as JSON and return it.
    """
    xml = event.get('body')
    if xml:
        xmldict = xmltodict.parse(xml)
        try:
            present, = (x for x in xmldict['wddxPacket']['item']
                        if x['@sequence'] == 'present')
            normalized = {v: present.get(k, '') for k, v in DAVID_MUSIC_ELEMS}
            return normalized
        except ValueError:
            return {"air_break": True}
