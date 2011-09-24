# coding: utf-8

import uuid, datetime

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated
from utils.constants import Fail, Success
from utils.imagepp import save_images
from utils.sp import sms_send
from utils.mkthings import generate_password

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
        data = self.get_data()

        info = Fail
        if 'password' in data and user.authenticate(data['password']):
            self.db.delete(user) # PS: delete all relation data
            self.db.commit()
            info = Success
        
        # delete user data 
        self.render_json(info)


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

class DelUserHandler(BaseRequestHandler):

    @authenticated
    def put(self, phn):
        user = self.current_user
        data = self.get_data()

        info = Fail
        if 'password' in data and user.authenticate(data['password']):
            self.db.delete(user) # PS: delete all relation data
            self.db.commit()
            info = Success
        
        # delete user data 
        self.render_json(info)

class UploadHandler(BaseRequestHandler):

    @authenticated
    def post(self):
        info = Fail
        if 'photo' in self.request.files:
            save_images(self.request.files['photo'])
            info = Success

        self.render_json(info)

class RestPasswordHandler(BaseRequestHandler):

    def get(self):
        info = Fail
        if not self.is_available_client():
            self.render_error(401)
            return
        else:
            user = User.query.get_by_phone(self.get_argument('p'))
            if user:
                new_password = generate_password()
                user.password = new_password
                user.save()
                sms_send(new_password)

                info = Success

        return self.render_json(info)

