import datetime
from mongoengine import (
    EmbeddedDocument,
    Document,
    StringField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    ReferenceField,
    IntField,
)


class FeedItem(EmbeddedDocument):
    id = StringField(required=True, unique=True)
    title = StringField(required=True)
    link = StringField(required=True)
    summary = StringField(required=True)
    published = DateTimeField()
    author = StringField()
    rights = StringField()
    updated = DateTimeField(default=datetime.datetime.now())


class Feed(Document):
    title = StringField(required=True)
    subtitle = StringField()
    language = StringField()
    updated = DateTimeField(default=datetime.datetime.now())
    ttl = IntField(default=360)
    logo = StringField()
    link = StringField(required=True, unique=True)
    items = ListField(EmbeddedDocumentField(FeedItem))


class User(Document):
    name = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    subscribed_feeds = ListField(ReferenceField(Feed))


class UserReadItem(Document):
    user = ReferenceField(User, required=True, unique_with=['item_id'])
    item_id = StringField(required=True)
