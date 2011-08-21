# coding: utf-8

import tornado.web

class BaseRequestHandler(tornado.web.RequestHandler):
    """the base RequestHandler for All."""

    def get_current_user(self):
        return self.get_secure_cookie("user")
