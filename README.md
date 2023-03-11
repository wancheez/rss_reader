# RSS Reader

RSS scraper application which saves RSS feeds to a database and lets a user view and manage feeds they’ve added to the system through an API.

## Features

User can sign up in the system, follow/unfollow new or existing feeds, list followed feeds, get followed feeds' content, mark content as seen and ignore it.
Feeds can be added to the system, feed content might be displayed, force update of a feed might be performed, failed to update feeds might be listed.


## Endpoints
- GET /docs - OpenAPI with all provided endpoints


## Synchronization

Feeds' content is being synchronized in an unattended manner with help of update-service.
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