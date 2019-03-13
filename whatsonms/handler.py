import json
import logging
from functools import wraps
from typing import Callable, Dict
from raven import Client

from whatsonms import config, dynamodb, v1


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
            message = json.dumps(
                {"data": {"type": "metadata", "id": "1", "attributes": message}}
            )
        response = {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": message,
        }
        dict.__init__(self, **response)


def normalize_request_path(path: str) -> str:
    """
    Args:
        path: The path provided in an AWS Lambda event.

    Returns:
        The path with trailing slash and URL_PREFIX removed.
    """
    return path.rstrip('/').replace(config.URL_PREFIX, '', 1)


def sentry(func: Callable) -> Callable:
    """
    Decorator that will forward exceptions + traces to sentry when the
    SENTRY_DSN environment variable is set.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        sentry = Client(environment=config.ENV, release=config.RELEASE)
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
    db = dynamodb.connect(config.DYNAMODB_TABLE)

    path = normalize_request_path(event['path'])
    verb = event['httpMethod']
    metadata = None

    if path == '/v1/update':
        metadata = v1.parse_metadata(event, verb)
        if metadata:
            db.set('whats-on', metadata)
    elif path == '/v1/whats-on':
        metadata = db.get('whats-on')

    if metadata:
        return Response(200, message=metadata)

    return Response(404, message='No metadata found')
