# coding: utf-8

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from apps import BaseRequestHandler
from apps.models import User, Loud

# TODO #1 object to json

class UserHandler(BaseRequestHandler):

    def get(self, phn):
        # TODO #3
        # empty '' string because for post create user
        user = User.query.get_by_phone(phn)

        #print vars(user)
        if user:
            # TODO ower test
            if user.ower_by(self.user):
                # user get the (content longitude latitude grade created phone name avatar last_longitude last_atitude
                # loud_num is_admin distance updated created)
                info = user.to_dict(exclude=['id', 'password', 'token', 'block'])
                info['loud_num'] = user.loud_num
                info['louds'] = [e.to_dict(exclude=['id', 'user_id', 'block']) for e in user.louds]
            else:
                # non self get the (phone, name, avatar, last_longitude, last_atitude, updated)
                info = user.to_dict(exclude=['id', 'password', 'token', 'radius', 'is_admin', 'block', 'created'])
        else:
            info = None

        self.render_json(info)

    def post(self, phn):
        # TODO #3 create user 
        data = self.get_data()
        self.render_json("doing")

    def put(self, phn):
        user = User.query.get_by_phone(phn)
        if user and user.ower_by(self.user):
            pass
        data = self.get_data()

        # TODO #3 create the update key=value strings
        self.render_json(data)

    def delete(self, phn):
        user = User.query.get_by_phone(phn)
        # PS: delete all relation data
        msg = {'status': 'fail'}
        if user and user.ower_by(self.user):
            self.db.delete(user)
            msg = {'status': 'success'}
        # delete user data 
        self.render_json(msg)


class AuthHandler(BaseRequestHandler):
    pass
