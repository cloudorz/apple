# coding: utf-8

import tornado.ioloop
import tornado.web

from apps import BaseRequestHandler

class HomeHandler(BaseRequestHandler):
    def get(self):
        says = "Hello Apple!"
        self.render("pages/home.html", hi=says)
        #self.write('Hello, apple')
