from flask import request
from mysql import connector as mysql_connector
import jwt
from datetime import datetime, timedelta
from functools import wraps
from . import db

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

def create_access_token(uid):
    token = jwt.encode({
        'user_id': uid,
        'exp': datetime.utcnow() + timedelta(days=100),
        'type': 'access'
    }, JWT_SECRET, JWT_ALGORITHM)
    return token

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM) 
        uid = payload['user_id']
        user = db.get_user(uid)
    except (KeyError, jwt.DecodeError, jwt.ExpiredSignatureError):
        raise Exception('Token is in incorrect form or expired')
    return user

def auth_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        bearer = request.headers.get('Authorization', None)
        if not bearer:
            return {'status': 'error', 'detail': 'Missing bearer token'}, 401

        token = bearer.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
            uid = payload['user_id']
            user = db.get_user(uid)
            return func(user=user, *args, **kwargs)

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return {'status': 'error', 'detail': 'Token is invaid or expired'}, 401
        except mysql_connector.Error:
            return {'status': 'error', 'detail': 'Server fail'}, 405
    
    return decorator
