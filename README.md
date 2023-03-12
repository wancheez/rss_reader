# RSS Reader

RSS scraper application which saves RSS feeds to a database and lets a user view and manage feeds they’ve added to the system through an API.

## Features

User can sign up in the system, follow/unfollow new or existing feeds, list followed feeds, get followed feeds' content, mark content as seen and ignore it.
Feeds can be added to the system, feed content might be displayed, force update of a feed might be performed, failed to update feeds might be listed.


## Swagger
- GET /docs - Swagger with all provided endpoints

# Example of use

User Interface:
1. POST /wancheez/register - Create a user with name wancheez
2. POST /wancheez/follow {"feed_url": "http://rss.cnn.com/rss/cnn_topstories.rss"} - Follow (and register) new Feed by User
3. GET /wancheez/feeds - Get user's feed list
4. GET /wancheez/feeditems - Get items from the feeds to which user has subscribed
5. POST /wancheez/feed_item/mark_read? {"item_id": "https://www.cnn.com/kamala-party/index.html"} - Mark feed item as read
6. GET /wancheez/feeditems?unread=True - Get unread items from the feeds to which user has subscribed
7. GET /wancheez/feed/items?unread=True&feed_id=640dce2a4ecda5b5b2fc2b6c - Get items of the particular feed (feed retrieved from /wancheez/feeds)
8. DELETE /wancheez/unfollow?feed_id=640dce2a4ecda5b5b2fc2b6c - Unfollow feed

Feed Interface:
1. POST /feed {"url": https://lifehacker.com/rss} - Add feed to the database
2. GET /feeds - Get all registered feeds
3. GET /feed/items?feed_url=https://lifehacker.com/rss - Get feed items of particular feed
4. POST /feed/update {"feed_url": "https://lifehacker.com/rss"} - Force update of the feed
5. GET /feeds/failed - Get all failed to update feeds


## Synchronization

Feeds' content is being synchronized in an unattended manner with help of update-service. Period of synchronization based on ttl-parameter of a feed.
In a several failed attempts, the synchronization process will be stopped. Manual synchronization will be required.
Failed to update feeds might be found in /feeds/failed.

## How to start

```
docker-compose build
docker-compose up
```

## Testing

In the root dir:
```
pytest
```

## Implementation details

The service is written with Python 3.x. 
MongoDB is used to store feeds info. MongoEngine as ORM.
Feed synchronization is implemented in the separate service with pydantic.
Redis is used as a broker for pydantic and storing attempts info.
The service is designed to be loose coupled with Representation, Model and Service layers.


## Configuration

If required, synchronization might be adjusted in the conf/conf.py file.


## TODO

Implement authorization with password.
Switch to async MongoDB ORM.