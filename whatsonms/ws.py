import boto3
import inspect
from functools import lru_cache, wraps
from typing import Callable

from whatsonms.http import Response


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
        # TODO: add connectionId to db
        return Response(200, message=event)

    @staticmethod
    @route('$disconnect')
    def disconnect(event):
        # TODO: remove connectionId from db
        return Response(200, message=event)

    @staticmethod
    @route('$default')
    def default(event):
        connection_id = event['requestContext']['connectionId']
        # TODO: scan db, publish message to all connectionIds

        ws_client = boto3.Session().client(
            'apigatewaymanagementapi',
            endpoint_url='https://{}/{}'.format(
                event['requestContext']['domainName'],
                event['requestContext']['stage']
            )
        )
        ws_client.post_to_connection(
            Data=b'updated metadata', ConnectionId=connection_id
        )
        return Response(200, message='message sent')
