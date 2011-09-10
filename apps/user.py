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
        user = User()
        data = self.get_data()
        user.from_dict(data)

        if user.save():
            msg = {'status': 'success'}
        else:
            msg = {'status': 'fail'}

        self.render_json(msg)

    @authenticated
    def put(self, phn):
        ''' The User object can't modify phone
        '''
        user = self.current_user

        data = self.get_data()
        user.from_dict(data)

        if user.save():
            msg = {'status': 'success'}
        else:
            msg = {'status': 'fail'}

        self.render_json(data)

    @authenticated
    def delete(self, phn):
        user = self.current_user
        
        self.db.delete(user) # PS: delete all relation data
        msg = {'status': 'success'}
        # delete user data 
        self.render_json(msg)


class AuthHandler(BaseRequestHandler):
    pass
