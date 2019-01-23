from functools import wraps
from typing import Callable, Dict
from raven import Client

import datetime
import json
import logging
import xmltodict
import urllib

from whatsonms.config import redis_client


DAVID_MUSIC_ELEMS = {
    'CDINFO.LABEL': 'mm_reclabel',
    'Music_CDID': 'catno',
    'Music_Composer': 'mm_composer1',
    'Music_MusicID': 'mm_uid',
    'USA.WNYC.ORCHESTRA': 'mm_ensemble1',
    'Title': 'title',
    'Music_Album': 'album',
    'USA.WNYC.SOLOIST1': 'mm_soloist1',
    'USA.WNYC.SOLOIST2': 'mm_soloist2',
    'USA.WNYC.SOLOIST3': 'mm_soloist3',
    'USA.WNYC.SOLOIST4': 'mm_soloist4',
    'USA.WNYC.SOLOIST5': 'mm_soloist5',
    'USA.WNYC.SOLOIST6': 'mm_soloist6',
    'USA.WNYC.CONDUCTOR': 'mm_conductor',
    'Time_RealStart': 'real_start_time',
    'Time_Start': 'start_time',
    'Time_Duration': 'length',
    'GUID': 'david_guid',
    }

DAVID_MUSIC_ELEMS_ITEMS = DAVID_MUSIC_ELEMS.items()

NEXGEN_MUSIC_ELEMS = {
    'number': 'mm_uid',
    'length': 'length',
    'composer': 'mm_soloist1',
    'licensor': 'mm_soloist2',
    'alt_artist': 'mm_ensemble1',
    'comment1': 'mm_composer1',
    'played_date': 'start_date',
    'played_time': 'start_time',
    'title': 'title',
    'album_title': 'album',
}

NEXGEN_MUSIC_ELEMS_ITEMS = NEXGEN_MUSIC_ELEMS.items()


class Response(dict):
    """
    Simple dictionary class that represents a standard Lambda response
    structure. Expires date is in UTC but specifies GMT based on RFC802
    3.3.1 saying, "For the purposes of HTTP, GMT is exactly equal to UTC".
    Args:
        status: An integer HTTP status code.
        message: A string message, default is empty.
        redirect: A redirect URL for the response, default is None.
    Raises:
        ValueError: A redirect was specified without a 301/302 status.
    """
    def __init__(self, status: int, message: str='', redirect: str=None):
        if message:
            message = json.dumps({'message': message})
        data = {
            'statusCode': status,
            'body': message,
        }
        if redirect:
            if status not in {301, 302}:
                raise ValueError('Must provide a 301/302 status with redirect.')
            data['headers'] = {
                                'location': redirect,
                                'Expires': datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
                                'Cache-Control': 'max-age=0, no-cache, no-store, must-revalidate, s-maxage=0, private',
                                'Pragma': 'no-cache',
                                'Content-Type': 'application/json',
                                }
        dict.__init__(self, **data)


def sentry(func: Callable) -> Callable:
    """
    Decorator that will forward exceptions + traces to sentry when the
    SENTRY_DSN environment variable is set.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        sentry = Client()
        with sentry.capture_exceptions():
            return func(*args, **kwargs)
    return wrapped


@sentry
def handler(event: Dict, context: Dict) -> Response:
    """
    The primary lambda handler.
    Args:
        event: A dictionary with a structure including query string parameters.
        context: A dictionary, the contents are not important.
    Returns:
        A 301 redirect to the appropriate Google DFP ad server with only a subset
        of those parameters in a specific order
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('Event: {}'.format(event))

    # parameters = event.get('queryStringParameters', None)

    path = event['path']
    verb = event['httpMethod']
    response = None

    if path == '/update':
        response = update_metadata(event, verb)
    elif path == '/whats-on':
        response = get_metadata(event)

    return response


def get_metadata(event: Dict) -> Response:
    """ Fetch cached JSON metadata from Redis
    """
    print('fetching from redis')
    return redis_client.get('whats-on')


def update_metadata(event: Dict, verb: str) -> Response:
    """ Import new metadata from DAVID or NexGen and save it to Redis.
    """
    metadata_json = import_metadata(event, verb)

    if metadata_json:
        redis_client.set('whats-on', metadata_json)
        print('*** saving to redis ***')
    else:
        print('*** No metadata_json ***')

    # This will return either the JSON, which will be discarded but signify
    # an OK response, or it will return None, signifying an error
    return metadata_json


def import_metadata(event: Dict, verb: str) -> str:
    """ Import new metadata from DAVID or NexGen, format it as JSON
        and return it.
    """
    if verb == 'GET':
        # Request is coming from NexGen
        if 'queryStringParameters' in event:
            xml = event['queryStringParameters']['xml_contents']
            xml = urllib.parse.unquote(xml)
        if xml:
            xmldict = xmltodict.parse(xml)
            # normalize the metadata from nexgen and david to look similar
            normalized = dict((v, (xmldict['audio'].get(k, u''))) for k, v in NEXGEN_MUSIC_ELEMS_ITEMS)
            return json.dumps(normalized)

    elif verb == 'POST':
        # Request is coming from DAVID
        if 'body' in event:
            xml = event['body']
        if xml:
            xmldict = xmltodict.parse(xml)
            # normalize the metadata from nexgen and david to look similar
            present = list(filter(lambda x: x['@sequence'] == 'present', xmldict['wddxPacket']['item']))
            normalized = dict((v, (present[0].get(k, u''))) for k, v in DAVID_MUSIC_ELEMS_ITEMS)
            return json.dumps(normalized)

    else:
        return None # error state

    return None # error state
