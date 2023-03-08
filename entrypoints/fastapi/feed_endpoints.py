from fastapi import APIRouter

from rss_reader.service_layer.feed_service import FeedService

router = APIRouter()
feed_service = FeedService()


@router.get("/feed/items")
def get_feed_items(feed_id: str):
    return feed_service.get_feed_items(feed_id)


@router.get("/feeds")
def get_feed_items():
    return feed_service.get_feeds()


@router.post("/feed")
async def add_feed(url: str):
    feed = feed_service.create_feed_from_url(url)
    return {"id": str(feed.id)}
