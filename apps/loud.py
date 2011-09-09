# coding: utf-8

from apps import BaseRequestHandler
from apps.models import User, Loud

class LoudHandler(BaseRequestHandler):
    def get(self, lid):
        loud = Loud.query.get_by_key(lid)
        loud_dict = loud.to_dict(exclude=['id', 'user_id', 'block'])
        # if you have line like this , 
        # there is a bug "self.render_json(loud.to_dict())" will be Oops
        loud_dict['user'] = loud.user.to_dict(exclude=['id', 'password', 'token', 'radius','updated', 'is_admin', 'block', 'created', 'last_lon', 'last_lat'])

        self.render_json(loud_dict)

    def post(self, lid):
        # TODO #1
        self.write("doing")

    def delete(self, lid):
        loud = Loud.query.get_by_key(lid)
        msg = {'status': 'fail'}
        if loud and loud.ower_by(self.user):
            self.db.delete(loud)
            msg = {'status': 'success'}

        self.render_json(msg)

class LoudSearchHandler(BaseRequestHandler):
    def get(self):
        # TODO #1 louds cycle set get
        louds = Loud.query.order_by('created desc').limit(1000)
        self.render_json("wait pls.")
