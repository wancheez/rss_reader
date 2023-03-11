import logging

from fastapi import HTTPException
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from rss_reader.dependency.containers import DependencyInjector
from rss_reader.domain.models import User

logger = logging.getLogger(__name__)

injector = DependencyInjector()


class UserService:
    def __init__(self, db_constructor=injector.provide("db")):
        db = db_constructor()
        info = db.server_info()
        logger.info(f"DB session created {info}")

    def register_user(self, name: str, email: str, password: str):
        user = User.objects(email=email).first()
        if user:
            raise HTTPException(status_code=400, detail="User exists")
        hashed_password = pbkdf2_sha256.hash(password)
        user = User(name=name, email=email, password=hashed_password)
        user.save()
        return user

    def login_user(self, email: str, password: str):
        user = User.objects(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not pbkdf2_sha256.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
