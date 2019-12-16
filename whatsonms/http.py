import inspect
from collections import defaultdict
from functools import lru_cache, wraps
from typing import Callable, Dict

import whatsonms.utils
from whatsonms import v1
from whatsonms.dynamodb import metadb


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
        """
        Handles updates from NexGen, which are received via GET requests
        with the data in the params.
        """
        metadata = v1.parse_metadata_nexgen(event)
        return _update(metadata, params)

    @staticmethod
    @route('POST', '/v1/update')
    def post_update(event, params):
        """
        Handles updates from DAVID, which are received via POST requests
        with the data in the request body.
        """
        stream = params.get('stream')
        metadata = v1.parse_metadata_david(event, stream)
        return _update(metadata, params)

    @staticmethod
    @route('GET', '/v1/whats-on')
    def get(event, params):
        """
        Handles a regular HTTP GET request from a client for the current
        metadata for a stream.
        """
        stream = params.get('stream')
        metadata = metadb.get_metadata(stream)
        if metadata:
            return whatsonms.utils.Response(200, data=metadata)
        return whatsonms.utils.Response(404, message='No metadata found')


def _update(metadata: dict, params: dict) -> whatsonms.utils.Response:
    stream = params.get('stream')
    if not metadata:
        print("No metadata found")
        return whatsonms.utils.Response(404, message='No metadata found')
    if not stream:
        print("Missing required parameter 'stream'")
        return whatsonms.utils.Response(
            500,
            message="Missing required parameter 'stream'"
        )

    metadata = metadb.set_metadata(stream, metadata)
    whatsonms.utils.broadcast(stream, data=metadata)
    return whatsonms.utils.Response(
        200,
        data=metadata,
        message=('Broadcast sent to %s subscribers' % stream)
    )
