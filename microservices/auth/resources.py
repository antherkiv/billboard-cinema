from falcon.media.validators import jsonschema
from falcon import HTTP_409, HTTP_201, HTTP_401
from sqlalchemy.sql import exists

from .schemas import user_schema
from .models import User
from .db import session


class Registration(object):
    @jsonschema.validate(user_schema)
    def on_post(self, req, resp):
        media = req.media.copy()
        if session.query(
                exists().where(User.username == media['username'])).scalar():
            resp.media = {
                "description":
                "User exists on our system, please login instead of register",
                "title":
                "User exists"
            }

            resp.status = HTTP_409

        else:
            user = User(**media)
            session.add(user)
            session.commit()

            resp.media = {'id': str(user.id)}

            resp.status = HTTP_201


class Token(object):
    @jsonschema.validate(user_schema)
    def on_post(self, req, resp):
        media = req.media.copy()
        user = session.query(User).filter_by(username=media['username']).one()

        if not (user and  user.check_password(media['password'])):
            resp.media = {
                "description":
                "User or password are incorrect",
                "title":
                "Unauthorized"
            }
            resp.status = HTTP_401

        else:
            from jose import jwt
            token = jwt.encode({'user': str(user.id)}, 'dracula', algorithm='HS256')

            resp.media = {'access_token': token, 'token_type': 'Bearer'}

            resp.status = HTTP_201




