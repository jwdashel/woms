from raven import Client
from typing import Callable
from functools import wraps
from whatsonms import config


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
