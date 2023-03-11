from fastapi import APIRouter

from rss_reader.service_layer.feed_service import FeedService
from rss_reader.service_layer.update_service import update_single_feed

router = APIRouter()
feed_service = FeedService()


@router.get("/feed/items")
def get_feed_items(url: str):
    """Get items of particular feed

    Args:
        url: Feed url

    Returns:
        feed items
    """
    return feed_service.get_feed_items(url)


@router.get("/feeds")
def get_feeds():
    """Get all available feeds

    Returns:
        Feeds
    """
    return feed_service.get_feeds()


@router.post("/feed")
def add_feed(url: str):
    """Add a new feed to the database

    Args:
        url: Feed url

    Returns:
        Created feed ID
    """
    feed = feed_service.create_feed_from_url(url)
    return {"id": str(feed.id)}


@router.post("/feed/update")
def update_feed_endpoint(url: str):
    """Force update of a feed by URL

    Args:
        url: Feed URL

    Returns:

    """
    update_single_feed.send(url)
    return {"message": "Update enqueued"}


@router.post("/feeds/failed")
def get_failed_feeds_endpoint():
    """List failed to update feeds

    Returns:
        failed to update feeds
    """
    feeds: list[str] = feed_service.get_failed_feeds()
    return {"failed_feeds": [feed.replace("feed:failed:", "") for feed in feeds]}
