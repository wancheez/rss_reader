import datetime
import time
import uuid
from functools import partial
from unittest.mock import patch

from conf.conf import SCHEDULER
from rss_reader.domain.models import Feed, FeedItem
from rss_reader.service_layer.feed_service import FeedService
from rss_reader.service_layer.update_service import (update_feeds,
                                                     update_single_feed)


def test_update_failed(mock_db, mock_redis):
    feed = _create_feed()
    mock_db()
    feed.save()
    cache_file = {}
    # try 3 times with failed result
    with patch(
        "rss_reader.service_layer.feed_service.FeedService.update_feed_items"
    ) as mock_upd:
        mock_upd.return_value = None
        for _ in range(SCHEDULER["MAX_RETRIES"]):
            update_single_feed(
                "http://test.com/new", partial(mock_redis, cache_file), mock_db,
            )

    # the feed will be marked as failed
    update_feeds(partial(mock_redis, cache_file), mock_db)
    feeds: list[str] = FeedService(
        mock_db, partial(mock_redis, cache_file)
    ).get_failed_feeds()
    assert "feed:failed:http://test.com/new" in feeds


def _create_feed():
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
    return feed1
