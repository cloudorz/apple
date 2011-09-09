# coding: utf-8

from apps import BaseRequestHandler
from apps.models import User, Loud

class LoudHandler(BaseRequestHandler):
    def get(self, lid):
        # TODO #1
        loud = Loud.query.get(lid)
        print dir(loud)
        self.render_json('ok')

    def post(self, lid):
        # TODO #1
        self.write("doing")

    def delete(self, lid):
        # FIXME if is owner
        loud = Loud.query.get(lid)
        msg = {'status': 'fail'}
        if user:
            self.db.delete(loud)
            msg = {'status': 'success'}

        self.render_json(msg)

class LoudSearchHandler(BaseRequestHandler):
    def get(self):
        # TODO #1 louds cycle set get
        louds = Loud.query.order_by('created desc').limit(1000)
        self.render_json("wait pls.")
