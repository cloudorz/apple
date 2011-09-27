# coding: utf-8

import functools

from tornado.web import HTTPError

def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user: 
            raise HTTPError(401)
        return method(self, *args, **kwargs)
    return wrapper

def availabelclient(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_available_client():
            raise HTTPError(401)
        return method(self, *args, **kwargs)
    return wrapper
