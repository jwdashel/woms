import pytest

from mockredis import mock_strict_redis_client


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    redis = mocker.patch('redis.StrictRedis', mock_strict_redis_client)
    yield redis
