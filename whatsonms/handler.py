import logging
from functools import wraps
from typing import Callable, Dict
from raven import Client

from whatsonms import config
from whatsonms.http import HttpRouter, Response
from whatsonms.ws import WebSocketRouter


logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    route_key = event.get('requestContext', {}).get('routeKey')
    path = normalize_request_path(event.get('path', ''))
    verb = event.get('httpMethod', '')

    if route_key:
        return WebSocketRouter.dispatch(route_key, event)
    elif verb and path:
        return HttpRouter.dispatch(verb, path, event)
