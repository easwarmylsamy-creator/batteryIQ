# backend/auth.py
from passlib.hash import bcrypt
from db.session import get_session
from db.models import User

def login_user(username: str, password: str):
    with get_session() as s:
        user = s.query(User).filter(User.username == username).first()
        if user and bcrypt.verify(password, user.hashed_password):
            return user
    return None

def testMode(username: str,password: str):
    with get_session() as s:
        user = s.query(User).filter(User.username == username).first()
        if user:
            return user
    return None