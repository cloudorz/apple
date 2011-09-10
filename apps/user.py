# coding: utf-8

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated


class UserHandler(BaseRequestHandler):

    @authenticated
    def get(self, phn):
        user = User.query.get_by_phone(phn)

        if user:
            info = user.user_to_dict(self.current_user)
        else:
            info = None

        self.render_json(info)

    def post(self, phn):
        # TODO #3 create user 
        data = self.get_data()
        self.render_json("doing")

    @authenticated
    def put(self, phn):
        user = User.query.get_by_phone(phn)
        if user and user.owner_by(self.current_user):
            pass
        data = self.get_data()

        # TODO #3 create the update key=value strings
        self.render_json(data)

    @authenticated
    def delete(self, phn):
        user = User.query.get_by_phone(phn)
        # PS: delete all relation data
        msg = {'status': 'fail'}
        if user and user.owner_by(self.current_user):
            self.db.delete(user)
            msg = {'status': 'success'}
        # delete user data 
        self.render_json(msg)


class AuthHandler(BaseRequestHandler):
    pass
