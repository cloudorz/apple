# coding: utf-8

import uuid, datetime

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated
from utils.constants import Fail, Success

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

        self.render_json(user.save() and Success or Fail)

    @authenticated
    def put(self, phn):
        ''' The User object can't modify phone
        '''
        user = self.current_user

        data = self.get_data()
        user.from_dict(data)

        self.render_json(user.save() and Success or Fail)

    @authenticated
    def delete(self, phn):
        user = self.current_user
        
        self.db.delete(user) # PS: delete all relation data
        # delete user data 
        self.render_json(Success)


class AuthHandler(BaseRequestHandler):

    def post(self):
        if not self.is_available_client():
            self.render_error(401)
            return
        else:
            new_info = self.get_data()
            if 'phone' in new_info and 'password' in new_info:
                user = User.query.get_by_phone(new_info['phone'])
                if user and user.authenticate(new_info['password']):
                    user.token = uuid.uuid5(uuid.NAMESPACE_URL, "%s%s" % (user.phone,
                        datetime.datetime.now())).hex
                    info = user.user_to_dict_by_auth()
                    user.save()
                else:
                    info = Fail
            else:
                info = Fail

        self.render_json(info) 

class PasswordHandler(BaseRequestHandler):

    @authenticated
    def post(self):
        data = self.get_data()

        info = Fail
        if 'new_password' in data and 'old_password' in data:
            if self.current_user.authenticate(data['old_password']):
                self.current_user.password = data['new_password'];
                self.current_user.save()

                info = Success

        self.render_json(info)
