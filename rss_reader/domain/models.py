import time

from mongoengine import (DateTimeField, Document, EmbeddedDocument,
                         EmbeddedDocumentField, FloatField, IntField,
                         ListField, ReferenceField, StringField)


class FeedItem(EmbeddedDocument):
    id = StringField(required=True, unique=True)
    title = StringField(required=True)
    link = StringField(required=True)
    summary = StringField()
    published = DateTimeField()
    author = StringField()
    rights = StringField()
    updated = FloatField(default=time.time())


class Feed(Document):
    title = StringField(required=True)
    subtitle = StringField()
    language = StringField()
    updated = FloatField(default=time.time())
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
    user = ReferenceField(User, required=True, unique_with=["item_id"])
    item_id = StringField(required=True)
