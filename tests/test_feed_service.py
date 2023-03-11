import datetime
import time
import uuid
from unittest.mock import patch

from rss_reader.domain.models import Feed, FeedItem
from rss_reader.service_layer.feed_service import FeedService
from tests.resources import PARSER_RESPONSE


def test_get_feed(mock_db):
    feed1, feed2 = _create_feeds()
    mock_db()
    feed1.save()
    feed2.save()
    feed_service = FeedService(mock_db)
    feed = feed_service.get_feed(title="TestFeed1")
    assert isinstance(feed, Feed)
    assert feed.id == feed1.id

    feed.delete()
    feed.save()
    feed = feed_service.get_feed(title="TestFeed1")
    assert not feed


def test_delete_feed(mock_db):
    feed1 = Feed(
        title="TestFeed1",
        subtitle="Subtitle",
        language="en",
        updated=time.time(),
        ttl=360,
        logo="http://123.jpg",
        link="http://test.com/new",
    )
    mock_db()
    feed1.save()
    feed_service = FeedService(mock_db)
    feed_service.delete_feed(feed1.id)
    feeds = Feed.objects().all()
    assert len(feeds) == 0


def test_get_feeds(mock_db):
    feed1, feed2 = _create_feeds()
    mock_db()
    feed1.save()
    feed2.save()
    feed_service = FeedService(mock_db)
    feeds = feed_service.get_feeds(serialized=False)
    assert len(feeds) == 2
    assert feed1.id == feeds[0].id and feed2.id == feeds[1].id


def test_create_feed_from_url(mock_db):
    feed_service = FeedService(mock_db)
    with patch("feedparser.parse") as mock_parse:
        mock_parse.return_value = PARSER_RESPONSE
        feed_service.create_feed_from_url("http://test.com")
    feeds = Feed.objects().all()
    assert len(feeds) == 1
    assert feeds[0].title == "Example Feed"


def test_get_feed_items(mock_db):
    mock_db()
    feed_item = FeedItem(
        id=str(uuid.uuid4()),
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
    feed1.save()
    feed_service = FeedService(mock_db)
    items = feed_service.get_feed_items(feed1.link)
    assert len(items) == 1
    assert items[0]["title"] == "test"


def _create_feeds():
    feed1 = Feed(
        title="TestFeed1",
        subtitle="Subtitle",
        language="en",
        updated=time.time(),
        ttl=360,
        logo="http://123.jpg",
        link="http://test.com/new",
    )
    feed2 = Feed(
        title="TestFeed2",
        subtitle="Subtitle",
        language="en",
        updated=time.time(),
        ttl=360,
        logo="http://123.jpg",
        link="http://test.com",
    )
    return feed1, feed2
