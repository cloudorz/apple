# coding: utf-8

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated

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
        msg = {'status': 'fail'}
        if data:
            u = User()
            u.user = self.current_user

            if self.current_user.is_admin:
                # admin's loud
                data['grade'] = 0

            u.from_dict(data)

            if u.can_save():
                self.db.commit()
                msg = {'status': 'success'}

        self.render_json(msg)

    @authenticated
    def delete(self, lid):
        loud = Loud.query.get_by_key(lid)
        msg = {'status': 'fail'}
        if loud and loud.owenr_by(self.current_user):
            self.db.delete(loud)
            msg = {'status': 'success'}

        self.render_json(msg)

class LoudSearchHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        # TODO #1 louds cycle set get
        louds = Loud.query.order_by('created desc').limit(1000)
        self.render_json("wait pls.")
