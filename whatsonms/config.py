from functools import lru_cache
import os

import redis


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)

# These settings are optional and will be strictly used for Sentry reporting.
RELEASE = os.environ.get('RELEASE', None)
ENV = os.environ.get('ENV', None)


@lru_cache()
def redis_client():
    return redis.StrictRedis(
        db=REDIS_DB,
        decode_responses=True,
        host=REDIS_HOST,
        port=REDIS_PORT,
    )
