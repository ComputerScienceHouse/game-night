from functools import wraps
from flask import abort, request, session

def requirequartermaster(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        from stuff import is_quartermaster
        if not is_quartermaster(session['userinfo']['preferred_username']):
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def require_read_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            from stuff import api_key_exists
            if not api_key_exists(request.headers['Authorization'][7:]):
                abort(403)
        except:
            abort(403)
        return function(*args, **kwargs)
    return wrapper