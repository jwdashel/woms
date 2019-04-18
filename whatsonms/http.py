import inspect
import json
from collections import defaultdict
from functools import lru_cache, wraps
from typing import Callable, Dict

from whatsonms import v1
from whatsonms.dynamodb import db


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
            message = jsonify_message(message)
        response = {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/vnd.api+json"
            },
            "body": message,
        }
        dict.__init__(self, **response)


def jsonify_message(message):
    return json.dumps(
        {"data": {"type": "metadata", "id": "1", "attributes": message}}
    )

def route(verb: str, path: str) -> Callable:
    """
    Decorator for use on HttpRouter static methods.
    Defines how a method should be dispatched.
    See the HttpRouter class docs for information.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.verb = verb.upper()
        wrapper.path = path
        return wrapper
    return decorator


class HttpRouter:
    """
    A simple HTTP router.
    To extend the router just add a new method like this:
        @staticmethod
        @route(VERB, PATH)
        def mymethod(event, params):
            <do stuff...>
    """
    @classmethod
    @lru_cache()
    def _dispatcher(cls):
        """
        Returns a function dispatch dictionary in the form:
            {
                'GET: {
                    '/path/1': get_func_1,
                    '/path/2': get_func_2,
                },
                'POST': {
                    '/path/1': post_func_1,
                },
            }

        This method is cached using lru_cache to prevent re-doing the
        class introspection on every call.
        """
        functions = (
            func for _, func in inspect.getmembers(cls, predicate=inspect.isfunction)
            if hasattr(func, 'verb') and hasattr(func, 'path')
        )
        dispatcher = defaultdict(dict)
        for func in functions:
            dispatcher[func.verb][func.path] = func

        return dispatcher

    @classmethod
    def dispatch(cls, verb: str, path: str, event: Dict):
        """
        Dispatches the function decorated with:
            @route(verb, path)
        """
        params = event.get('queryStringParameters', {})
        return cls._dispatcher()[verb.upper()][path](event, params)

    @staticmethod
    @route('GET', '/v1/update')
    def get_update(event, params):
        metadata = v1.parse_metadata_nexgen(event)
        stream_slug = params.get('stream')
        if metadata and stream_slug:
            db.set(stream_slug, metadata)
            return Response(200, message=metadata)
        return Response(404, message='No metadata found')

    @staticmethod
    @route('POST', '/v1/update')
    def post_update(event, params):
        metadata = v1.parse_metadata_david(event)
        stream_slug = params.get('stream')
        if metadata and stream_slug:
            db.set(stream_slug, metadata)
            return Response(200, message=metadata)
        return Response(404, message='No metadata found')

    @staticmethod
    @route('GET', '/v1/whats-on')
    def get(event, params):
        stream_slug = params.get('stream')
        metadata = db.get(stream_slug)
        if metadata:
            return Response(200, message=metadata)
        return Response(404, message='No metadata found')