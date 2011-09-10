# coding: utf-8

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated
from utils.constants import Fail, Success

class LoudHandler(BaseRequestHandler):

    @authenticated
    def get(self, lid):
        loud = Loud.query.get_by_key(lid)

        if loud:
            loud_dict = loud.loud_to_dict()
        else:
            loud_dict = None

        self.render_json(loud_dict)

    @authenticated
    def post(self, lid):
        data = self.get_data()
        msg = Fail
        if data:
            loud = Loud()
            loud.user = self.current_user

            if self.current_user.is_admin:
                # admin's loud
                data['grade'] = 0

            loud.from_dict(data)

            if loud.save():
                msg = Success

        self.render_json(msg)

    @authenticated
    def delete(self, lid):
        loud = Loud.query.get_by_key(lid)
        msg = Fail
        if loud and loud.owenr_by(self.current_user):
            self.db.delete(loud)
            msg = Success

        self.render_json(msg)

class LoudSearchHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        louds = Loud.query.get_by_cycle(self.current_user)
        loud_dicts = [e.to_dict() for e in louds]

        self.render_json(loud_dicts)
