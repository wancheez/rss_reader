import datetime
import json
import logging
import time
import uuid
from time import mktime
from typing import Optional

import feedparser
from fastapi import HTTPException
from mongoengine.errors import ValidationError
from url_normalize import url_normalize

from rss_reader.dependency.containers import DependencyInjector
from rss_reader.domain.models import Feed, FeedItem, User, UserReadItem

logger = logging.getLogger(__name__)
injector = DependencyInjector()


class FeedService:
    """Feeds Manipulating"""
    def __init__(
        self,
        db_constructor=injector.provide("db"),
        redis_constructor=injector.provide("redis"),
    ):
        db = db_constructor()
        info = db.server_info()
        self._redis = redis_constructor()
        logger.debug(f"DB session created {info}")

    def get_feed(self, **filters) -> Optional[Feed]:
        feed_object = Feed.objects(**filters).first()
        if feed_object:
            return feed_object
        else:
            return None

    def get_feeds(self, serialized=True):
        """Get all available feeds"""
        feeds = Feed.objects().exclude("items")
        feed_list = [feed for feed in feeds]
        if serialized:
            return [json.loads(feed.to_json()) for feed in feed_list]
        return feed_list

    def update_feed_items(self, feed: Feed):
        """Update feed items.
        Used for updating feed content.
        """
        link = feed.link
        updated_feed = self._download_feed(link)
        feed.updated = time.time()
        feed.items = updated_feed.items
        self._redis.set(f"feed:updated:{feed.link}", feed.updated)
        self._redis.set(f"feed:retries:{feed.link}", 0)
        self._redis.delete(f"feed:failed:{feed.link}")
        logger.info(f"Feed {feed.link} updated")
        feed.save()

    def create_feed_from_url(self, url: str) -> Feed:
        url = url_normalize(url)
        feed = self.get_feed(link=url)
        if feed:
            return feed
        feed = self._download_feed(url)
        feed.save()
        self._redis.set(f"feed:updated:{feed.link}", feed.updated)
        logger.info(f"Feed {feed.link} created")
        return feed

    def delete_feed(self, feed_id: str) -> None:
        feed = Feed.objects(id=feed_id).first()
        if not feed:
            raise HTTPException(status_code=404)
        Feed.delete(feed)

    def get_feed_items(self, url: str):
        feed = Feed.objects(link=url).first()
        if feed:
            return [i.to_mongo() for i in feed.items]
        else:
            raise HTTPException(status_code=404, detail="Feed not found")

    def _download_feed(self, url: str):
        d = feedparser.parse(url)
        if d.get("bozo", 1) == 1:
            raise HTTPException(
                status_code=400, detail="Could not parse the RSS feed. Bad Format."
            )
        feed_items = []
        for entry in d.get("entries", ()):
            date_parsed = entry.get("published_parsed", None)
            feed_items.append(
                FeedItem(
                    id=entry.get("id", str(uuid.uuid4())),
                    title=entry.get("title"),
                    link=entry.get("link"),
                    summary=entry.get("summary"),
                    published=datetime.datetime.fromtimestamp(
                        mktime(date_parsed),
                    )
                    if date_parsed
                    else datetime.datetime.now(),
                    author=entry.get("author"),
                    rights=entry.get("rights"),
                )
            )
        feed_info = d.get("feed")
        if not feed_info:
            raise HTTPException(status_code=400, detail="Feed object is invalid")
        feed = Feed(
            title=feed_info.get("title", "No title"),
            subtitle=feed_info.get("subtitle", "No subtitle"),
            link=url,
            language=feed_info.get("language", "en"),
            updated=time.time(),
            ttl=feed_info.get("ttl", 60),
            logo=feed_info.get("logo", url),
            items=feed_items,
        )
        return feed

    def get_failed_feeds(self):
        failed = self._redis.keys("feed:failed:*")
        return failed


class UserFeedService:
    """User's feed manipulating"""
    def __init__(self, db_constructor=injector.provide("db")):
        db = db_constructor()
        info = db.server_info()
        self.feed_service = FeedService(db_constructor)
        logger.info(f"DB session created {info}")

    def mark_item_as_read(self, user_name: str, item_id: str) -> None:
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with name {user_name} does not exist"
            )
        item_exists = UserReadItem.objects(user=user, item_id=item_id).first()
        if not item_exists:
            feed_item = UserReadItem(user=user, item_id=item_id)
            feed_item.save()

    def get_user_feeds_items(
        self, user_name: str, just_unread: bool = False, feed_id: str = None
    ):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with name {user_name} does not exist"
            )
        if feed_id:
            try:
                feeds = [
                    Feed.objects(
                        id=feed_id, id__in=[feed.id for feed in user.subscribed_feeds]
                    ).first()
                ]
                if not feeds:
                    raise HTTPException(status_code=404, detail=f"Feed not found")
            except ValidationError:
                raise HTTPException(status_code=404, detail=f"Feed not found")
        else:
            feeds = Feed.objects(
                id__in=[feed.id for feed in user.subscribed_feeds],
            )

        result = []
        if just_unread:
            read_items = UserReadItem.objects(user=user).all()
            read_ids = [read_item.item_id for read_item in read_items]
            for feed in feeds:
                for feed_item in feed.items:
                    if feed_item.id not in read_ids:
                        result.append(json.loads(feed_item.to_json()))
            return result

        for feed in feeds:
            for feed_item in feed.items:
                result.append(json.loads(feed_item.to_json()))
        return result

    def follow_feed(self, feed_url: str, user_name: str):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with name {user_name} does not exist"
            )
        feed = Feed.objects(link=feed_url).first()
        if not feed:
            feed = self.feed_service.create_feed_from_url(feed_url)
        if feed not in user.subscribed_feeds:
            user.subscribed_feeds.append(feed)
            user.save()

    def unfollow_feed(self, feed_id: str, user_name: str):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with name {user_name} does not exist"
            )
        feed = Feed.objects(
            id=feed_id, id__in=[feed.id for feed in user.subscribed_feeds]
        ).first()
        if not feed:
            raise HTTPException(
                status_code=404, detail=f"User doesn't follow this feed"
            )
        user.update(pull__subscribed_feeds=feed)
        user.save()

    def get_user_feeds(self, user_name: str):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User with name {user_name} does not exist"
            )
        feeds = Feed.objects(
            id__in=[feed.id for feed in user.subscribed_feeds]
        ).exclude("items")
        feed_list = [feed for feed in feeds]
        return [json.loads(feed.to_json()) for feed in feed_list]
