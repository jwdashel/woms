import inspect
from functools import lru_cache, wraps
from typing import Callable

from whatsonms.http import Response


def route(route_key: str) -> Callable:
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
        return {
            func.route_key: func
            for _, func in inspect.getmembers(cls, predicate=inspect.isfunction)
            if hasattr(func, 'route_key')
        }

    @classmethod
    def dispatch(cls, route_key, event):
        return cls._dispatcher()[route_key](event)

    @staticmethod
    @route('$connect')
    def connect(event):
        return Response(200, message=event)

    @staticmethod
    @route('$disconnect')
    def disconnect(event):
        return Response(200, message=event)

    @staticmethod
    @route('$default')
    def default(event):
        return Response(200, message=event)
