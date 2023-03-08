
from fastapi import HTTPException
from mongoengine import connect
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from rss_reader.domain.models import User

class UserService:
    def __init__(self):
        connect('rss', host='mongodb://mongo:mongo@localhost', port=27017, )

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


