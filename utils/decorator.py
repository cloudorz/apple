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

def admin(label_name, obj_name):
    ''' need admin right
    You must define the get_recipient method and recipient member
    in RequestHandler
    '''
    def inneradmin(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            obj = self.get_recipient(kwargs.pop(label_name, None))
            if not (obj and obj.admin_by(self.current_user)):
                raise HTTPError(403)
            kwargs[obj_name] = obj
            return method(self, *args, **kwargs)
        return wrapper
    return inneradmin

def owner(label_name, obj_name):
    ''' need owner right
    You must define the get_recipient method and recipient member
    in RequestHandler
    '''
    def innerowner(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            obj = self.get_recipient(kwargs[label_name])
            if not (obj and obj.owner_by(self.current_user)):
                raise HTTPError(403)
            kwargs[obj_name] = obj
            return method(self, *args, **kwargs)
        return wrapper
    return innerowner
