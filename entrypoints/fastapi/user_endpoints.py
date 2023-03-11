from fastapi import APIRouter

from rss_reader.service_layer.feed_service import UserFeedService
from rss_reader.service_layer.user_service import UserService

router = APIRouter()


user_feed_service = UserFeedService()
user_service = UserService()


@router.post("/{user_name}/feed_item/mark_read")
def mark_feed_item_read(item_id: str, user_name: str):
    """Mark feed item as read

    Args:
        item_id: Item ID
        user_name: Username

    Returns:
        Result message
    """
    user_feed_service.mark_item_as_read(user_name, item_id)
    return {"message": "Item has been marked"}


@router.get("/{user_name}/feed/items")
def get_feed_items_by_user_and_feed(user_name: str, feed_id: str, unread: bool = False):
    """Ger feed items of a particular feed for a user

    Args:
        user_name: Username
        feed_id: Feed ID
        unread: Fetch just unread

    Returns:
        List of feed items
    """
    return user_feed_service.get_user_feeds_items(user_name, unread, feed_id)


@router.post("/{user_name}/register")
def register_user(user_name: str, email: str, password: str):
    """Register new user

    Args:
        user_name: Username
        email: Email
        password: Password

    Returns:
        Result message
    """
    user_service.register_user(user_name, email, password)
    return {"message": "User registered successfully"}


@router.post("/{user_name}/follow")
def follow_feed(feed_url: str, user_name: str):
    """Follow feed

    Args:
        feed_url: Feed url
        user_name: Username

    Returns:
        Result message
    """
    user_feed_service.follow_feed(feed_url, user_name)
    return {"message": "User now subscribed to feed"}


@router.delete("/{user_name}/unfollow")
def unfollow_feed(feed_id: str, user_name: str):
    """Unfollow feed

    Args:
        feed_id: Feed id
        user_name: Username

    Returns:
        Result message
    """
    user_feed_service.unfollow_feed(feed_id, user_name)
    return {"message": "Feed has been unfollowed"}


@router.get("/{user_name}/feeds")
def get_user_feeds(user_name: str):
    """List all user feeds

    Args:
        user_name: Username

    Returns:
        List of user feeds
    """
    return user_feed_service.get_user_feeds(user_name)


@router.get("/{user_name}/feeditems")
def get_user_feed_items(user_name: str, unread=False):
    """List feed items for subscribed feeds

    Args:
        user_name: Username
        unread: Fetch just unread

    Returns:
        List of feed items
    """
    return user_feed_service.get_user_feeds_items(user_name, unread)
