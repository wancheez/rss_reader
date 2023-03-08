import json

from mongoengine.errors import ValidationError
from url_normalize import url_normalize
import datetime
import uuid
from time import mktime
from typing import Optional
from fastapi import HTTPException
import feedparser
from mongoengine import connect

from rss_reader.domain.models import User, Feed, FeedItem, UserReadItem


class FeedService:
    def __init__(self):
        connect('rss', host='mongodb://mongo:mongo@localhost', port=27017)

    def get_feed(self, **filters) -> Optional[Feed]:
        feed_object = Feed.objects(**filters).first()
        if feed_object:
            return feed_object
        else:
            return None

    def get_feeds(self):
        feeds = Feed.objects().exclude("items")
        feed_list = [feed for feed in feeds]
        return [json.loads(feed.to_json()) for feed in feed_list]

    def update_feed_items(self, feed: Feed):
        pass

    def create_feed_from_url(self, url: str) -> Feed:
        url = url_normalize(url)
        feed = self.get_feed(link=url)
        if feed:
            return feed
        d = feedparser.parse(url)
        feed_items = []
        for entry in d.get("entries", ()):
            date_parsed = entry.get("published_parsed", None)
            feed_items.append(
                FeedItem(
                    id=entry.get("id", uuid.uuid4()),
                    title=entry.get("title"),
                    link=entry.get("link"),
                    summary=entry.get("summary"),
                    published=datetime.datetime.fromtimestamp(mktime(date_parsed)),
                    author=entry.get("author"),
                    rights=entry.get("rights"),
                )
            )
        feed_info = d.get("feed")
        if not feed_info:
            raise HTTPException(status_code=400, detail="Feed object is invalid")
        date_updated = feed_info.get("updated_parsed", None)
        feed = Feed(
            title=feed_info.get("title", "No title"),
            subtitle=feed_info.get("subtitle", "No subtitle"),
            link=url,
            language=feed_info.get("language", "en"),
            updated=datetime.datetime.fromtimestamp(mktime(date_updated)),
            ttl=feed_info.get("ttl", 60),
            logo=feed_info.get("logo", url),
            items=feed_items,
        )
        feed.save()
        return feed

    def delete_feed(self, feed_id: str) -> None:
        feed = Feed.objects(id=feed_id)
        if not feed:
            raise HTTPException(status_code=404)
        Feed.delete(feed)

    def get_feed_items(self, feed_id: str):
        feed = Feed.objects(id=feed_id).first()
        if feed:
            return [i.to_mongo() for i in feed.items]
        else:
            raise HTTPException(status_code=404, detail="Feed not found")


class UserFeedService:
    def __init__(self):
        connect('rss', host='mongodb://mongo:mongo@localhost', port=27017)
        self.feed_service = FeedService()

    def mark_item_as_read(self, user_name: str, item_id: str) -> None:
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with name {user_name} does not exist")
        item_exists = UserReadItem.objects(user=user, item_id=item_id).first()
        if not item_exists:
            feed_item = UserReadItem(user=user, item_id=item_id)
            feed_item.save()

    def get_user_feeds_items(self, user_name: str, just_unread: bool = False, feed_id: str = None):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with name {user_name} does not exist")
        if feed_id:
            try:
                feeds = [Feed.objects(id=feed_id, id__in=[feed.id for feed in user.subscribed_feeds]).first()]
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
            raise HTTPException(status_code=404, detail=f"User with name {user_name} does not exist")
        feed = Feed.objects(link=feed_url).first()
        if not feed:
            feed = self.feed_service.create_feed_from_url(feed_url)
        if feed not in user.subscribed_feeds:
            user.subscribed_feeds.append(feed)
            user.save()

    def unfollow_feed(self, feed_id: str, user_name: str):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with name {user_name} does not exist")
        feed = Feed.objects(id=feed_id, id__in=[feed.id for feed in user.subscribed_feeds]).first()
        if not feed:
            raise HTTPException(status_code=404, detail=f"User doesn't follow this feed")
        user.update(pull__subscribed_feeds=feed)
        user.save()

    def get_user_feeds(self, user_name: str):
        user = User.objects(name=user_name).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with name {user_name} does not exist")
        feeds = Feed.objects(id__in=[feed.id for feed in user.subscribed_feeds]).exclude("items")
        feed_list = [feed for feed in feeds]
        return [json.loads(feed.to_json()) for feed in feed_list]
