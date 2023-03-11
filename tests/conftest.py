from functools import partial

import mongomock
import pytest as pytest
from mongoengine import connect, disconnect


class MockRedis:
    def __init__(self, cache=dict()):
        self.cache = cache

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        return None  # return nil

    def set(self, key, value, *args, **kwargs):
        if self.cache:
            self.cache[key] = value
            return "OK"
        return None  # return nil in case of some issue

    def incr(self, key):
        val = self.cache.get(key, 0)
        self.cache[key] = val + 1

    def keys(self, *args, **kwargs):
        return list(self.cache.keys())


@pytest.fixture
def mock_db():
    yield partial(
        connect,
        db="mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )
    disconnect()


@pytest.fixture
def mock_redis():
    yield partial(
        MockRedis,
    )
