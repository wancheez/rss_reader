from functools import partial

import redis
from mongoengine import connect

from conf.conf import MONGO, REDIS


class DependencyInjector:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DependencyInjector, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        db_connector = partial(
            connect,
            db=MONGO.get("database"),
            host=MONGO.get("host", "mongo"),
            port=MONGO.get("port", 27017),
            username=MONGO.get("username"),
            password=MONGO.get("password"),
        )
        redis_connector = partial(
            redis.StrictRedis,
            host=REDIS.get("host", "redis"),
            port=REDIS.get("port", 6379),
            db=REDIS.get("db", 0),
            charset="utf-8",
            decode_responses=True,
        )

        self._deps = {
            "db": db_connector,
            "redis": redis_connector,
        }

    def provide(self, dep_type):
        if dep := self._deps.get(dep_type):
            return dep
        raise ValueError(f"Dependency for {dep_type} is not configured")
