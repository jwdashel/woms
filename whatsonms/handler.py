from functools import wraps
from typing import Callable, Dict
from raven import Client

import datetime
import json
import logging
import xmltodict
import urllib


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

    if 'queryStringParameters' in event:
        xml = event['queryStringParameters']['xml_contents']
        xml = urllib.parse.unquote(xml)

    if xml:
        xmldict = xmltodict.parse(xml)
        j = json.dumps(xmldict)
        return j

    return None
