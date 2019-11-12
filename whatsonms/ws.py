import inspect
import simplejson as json
from functools import lru_cache, wraps
from typing import Callable

from whatsonms.dynamodb import metadb, subdb
from whatsonms.utils import broadcast, Response


def route(route_key: str) -> Callable:
    """
    Decorator for use on WebSocketRouter static methods.
    Defines how a method should be dispatched.
    See the WebSocket class docs for information.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.route_key = route_key
        return wrapper
    return decorator


class WebSocketRouter:
    """
    A simple WebSocket router.
    To extend the router just add a new method like this:
        @staticmethod
        @route(ROUTE_KEY)
        def mymethod(event):
            <do stuff...>
    """
    @classmethod
    @lru_cache()
    def _dispatcher(cls):
        """
        Returns a function dispatch dictionary in the form:
            {
                'route_key_1': route_func_1,
                'route_key_2': route_func_2,
            }

        This method is cached using lru_cache to prevent re-doing the
        class introspection on every call.
        """
        return {
            func.route_key: func
            for _, func in inspect.getmembers(cls, predicate=inspect.isfunction)
            if hasattr(func, 'route_key')
        }

    @classmethod
    def dispatch(cls, route_key, event):
        """
        Dispatches the function decorated with:
            @route(route_key)
        """
        return cls._dispatcher()[route_key](event)

    @staticmethod
    @route('$connect')
    def connect(event):
        """
        AWS API Gateway calls this route when a client connects via WebSockets.
        """
        connection_id = event['requestContext']['connectionId']
        stream = event['queryStringParameters']['stream']
        subdb.subscribe(stream, connection_id)
        return Response(200)

    @staticmethod
    @route('$disconnect')
    def disconnect(event):
        """
        AWS API Gateway calls this route when a WebSocket client disconnects.
        """
        connection_id = event['requestContext']['connectionId']
        subdb.unsubscribe(connection_id)
        return Response(200)

    @staticmethod
    @route('$default')
    def default(event):
        """
        Route a WebSocket client calls after initial connect to get back the
        latest metdata for a stream.
        """
        connection_id = event['requestContext']['connectionId']
        body = json.loads(event['body'])
        stream = body['data']['stream']
        metadata = metadb.get_metadata(stream)
        broadcast(stream, recipient_ids=[connection_id], data=metadata)
        return Response(200)
