import json
import logging
import urllib
import xmltodict
from functools import wraps
from typing import Callable, Dict
from raven import Client

from whatsonms.config import ENV, RELEASE, redis_client


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


class Response(dict):
    """
    Simple dictionary class that represents a standard Lambda response
    structure.
    Args:
        status: An integer HTTP status code.
        message: A string containing the metadata JSON, default is empty.
    """
    def __init__(self, status: int, message: str = ''):
        if message:
            message = json.dumps({'message': message})
        data = {
            'statusCode': status,
            'body': message,
        }
        dict.__init__(self, **data)


def sentry(func: Callable) -> Callable:
    """
    Decorator that will forward exceptions + traces to sentry when the
    SENTRY_DSN environment variable is set.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        sentry = Client(environment=ENV, release=RELEASE)
        with sentry.capture_exceptions():
            return func(*args, **kwargs)
    return wrapped


@sentry
def handler(event: Dict, context: Dict) -> Response:
    """
    The primary lambda handler.
    Args:
        event: A dictionary with a structure including query string parameters
            and path.
        context: A dictionary, the contents are not important.
    Returns:
        A JSON string, which will be discarded but signify an OK response,
        or None, which will signify an error.
    """
    logger.info('Event: {}'.format(event))

    path = event['pathParameters']['proxy']
    verb = event['httpMethod']
    metadata = None

    if path == '/update':
        metadata = set_metadata(event, verb)
    elif path == '/whats-on':
        metadata = get_metadata()

    if metadata:
        return Response(200, message=metadata)

    return Response(404, message='No metadata found')


def get_metadata() -> Dict:
    """ Fetch cached JSON metadata from Redis
    """
    client = redis_client()
    metadata = json.loads(client.get('whats-on'))
    return metadata


def set_metadata(event: Dict, verb: str) -> Dict:
    """ Import new metadata from DAVID or NexGen and save it to Redis.
    """
    metadata = parse_metadata(event, verb)
    client = redis_client()

    if metadata:
        client.set('whats-on', json.dumps(metadata, sort_keys=True))
    else:
        logger.error('Error: no metadata JSON to save')

    # This will return either the JSON, which will be discarded but signify
    # an OK response, or it will return None, signifying an error
    return metadata


def parse_metadata(event: Dict, verb: str) -> Dict:
    """ Parse new metadata from DAVID or NexGen -- format it as JSON
        and return it.
    """
    if verb == 'GET':
        # Request is coming from NexGen
        if 'queryStringParameters' in event:
            xml = event['queryStringParameters']['xml_contents']
            xml = urllib.parse.unquote(xml)
        if xml:
            xmldict = xmltodict.parse(xml)
            normalized = {
                v: xmldict['audio'].get(k, '') for k, v in NEXGEN_MUSIC_ELEMS
            }
            return normalized

    elif verb == 'POST':
        # Request is coming from DAVID
        if 'body' in event:
            xml = event['body']
        if xml:
            xmldict = xmltodict.parse(xml)
            present, = (x for x in xmldict['wddxPacket']['item']
                        if x['@sequence'] == 'present')
            normalized = {v: present.get(k, '') for k, v in DAVID_MUSIC_ELEMS}
            return normalized

    else:
        return None
