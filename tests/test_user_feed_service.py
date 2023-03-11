import datetime
import time
import uuid

from rss_reader.domain.models import Feed, FeedItem, User, UserReadItem
from rss_reader.service_layer.feed_service import UserFeedService


def test_mark_item_as_read(mock_db):
    user, feed = _create_user_and_feed()
    mock_db()
    user.save()
    feed.save()
    user_feed = UserFeedService(mock_db)
    user_feed.mark_item_as_read(user.name, feed.items[0].id)
    user_read_item = UserReadItem.objects().first()
    user_read_item.user = user
    user_read_item.item_id = feed.items[0].id


def test_get_user_feeds_items(mock_db):
    user, feed = _create_user_and_feed()
    mock_db()
    feed.save()
    user.subscribed_feeds = [feed]
    user.save()

    user_feed = UserFeedService(mock_db)
    user_feeds_items = user_feed.get_user_feeds_items(user.name)
    assert len(user_feeds_items) == 1
    assert user_feeds_items[0]["id"] == feed.items[0].id


def test_follow_unfollow_feed(mock_db):
    user, feed = _create_user_and_feed()
    mock_db()
    user.save()
    feed.save()
    user_feed = UserFeedService(mock_db)
    user_feed.follow_feed(feed.link, user.name)
    user_feeds_items = user_feed.get_user_feeds_items(user.name)
    assert len(user_feeds_items) == 1
    assert user_feeds_items[0]["id"] == feed.items[0].id
    user_feed.unfollow_feed(feed.id, user.name)
    user_feeds_items = user_feed.get_user_feeds_items(user.name)
    assert len(user_feeds_items) == 0


def test_user_feeds(mock_db):
    user, feed = _create_user_and_feed()
    mock_db()
    user.save()
    feed.save()
    user_feed = UserFeedService(mock_db)
    user_feed.follow_feed(feed.link, user.name)
    feeds = user_feed.get_user_feeds(user.name)
    assert len(feeds) == 1
    assert feeds[0]["title"] == "TestFeed1"


def _create_user_and_feed():
    user = User(name="test_user", email="test@example.com", password="password123")
    feed_item_id = str(uuid.uuid4())
    feed_item = FeedItem(
        id=feed_item_id,
        title="test",
        link="test",
        summary="test",
        author="test",
        rights="test",
        published=datetime.datetime.now(),
        updated=time.time(),
    )
    feed1 = Feed(
        title="TestFeed1",
        subtitle="Subtitle",
        language="en",
        updated=time.time(),
        ttl=360,
        logo="http://123.jpg",
        link="http://test.com/new",
        items=[feed_item],
    )
    return user, feed1
