import logging
import time

import dramatiq
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dramatiq.brokers.redis import RedisBroker

from conf.conf import SCHEDULER
from rss_reader.dependency.containers import DependencyInjector
from rss_reader.service_layer.feed_service import FeedService
from conf.conf import REDIS

injector = DependencyInjector()
logger = logging.getLogger(__name__)

url_str = f"redis://{REDIS.get('host')}:{REDIS.get('port')}"
dramatiq.set_broker(RedisBroker(url=url_str))


@dramatiq.actor
def update_feeds(
        redis_constructor=injector.provide("redis"), db_constructor=injector.provide("db")
):
    """Update all feeds from DB"""
    feed_service = FeedService(db_constructor)
    feeds = feed_service.get_feeds(serialized=False)
    redis = redis_constructor()
    for feed in feeds:
        feed_updated = redis.get(f"feed:updated:{feed.link}")
        if not feed_updated:
            feed_updated = time.time()
            redis.set(f"feed:updated:{feed.link}", time.time() - feed.ttl)
        else:
            feed_updated = float(feed_updated)
        retry_count = redis.get(f"feed:retries:{feed.link}")
        retry_count = int(retry_count) if retry_count else 0
        if retry_count >= SCHEDULER["MAX_RETRIES"]:
            redis.set(f"feed:failed:{feed.link}", "1")
            logger.warning(f"Feed {feed.link} failed to update")
        elif time.time() - feed_updated > feed.ttl:
            logger.info("Run update feeds")
            update_single_feed.send(feed.link)


@dramatiq.actor(max_retries=SCHEDULER["MAX_RETRIES"])
def update_single_feed(
        url: str,
        redis_constructor=injector.provide("redis"),
        db_constructor=injector.provide("db"),
):
    """Update feed by URL. Ignores failed property"""
    redis = redis_constructor()
    redis.incr(f"feed:retries:{url}")
    feed_service = FeedService(db_constructor)
    feed = feed_service.get_feed(link=url)
    if feed:
        feed_service.update_feed_items(feed)


def run_scheduling():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=update_feeds.send,
        trigger=CronTrigger.from_crontab(SCHEDULER["RUN_INTERVAL"]),
    )
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
