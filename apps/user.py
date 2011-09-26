# coding: utf-8

import uuid, datetime

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated, availabelclient
from utils.constants import Fail, Success
from utils.imagepp import save_images
from utils.sp import sms_send, ret_code2desc
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

    @availabelclient
    def post(self, phn):
        user = User()
        data = self.get_data()
        data['avatar'] = 'i/%s.jpg' % data['phone'] 
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
        # PS: delete all relation data user_id = 0
        self.db.delete(self.current_user) 
        self.db.commit()
        
        # delete user data 
        self.render_json(Success)


class AuthHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        new_info = self.get_data()
        info = Fail
        if 'phone' in new_info and 'password' in new_info:
            user = User.query.get_by_phone(new_info['phone'])
            if user and user.authenticate(new_info['password']):
                user.token = uuid.uuid5(uuid.NAMESPACE_URL, "%s%s" % (user.phone,
                    datetime.datetime.now())).hex
                info = user.user_to_dict_by_auth() # must before save
                user.save()

        self.render_json(info) 


class PasswordHandler(BaseRequestHandler):

    @authenticated
    def get(self):
        pw = self.get_argument('pw')

        self.render_json(self.current_user.authenticated(pw) and Success or Fail)

    @availabelclient
    def post(self):
        info = Fail
        user = User.query.get_by_phone(self.get_argument('p'))
        if user:
            new_password = generate_password()

            if sms_send(user.phone, {'name': user.name, 'password': new_password}, 2) > 0:
                user.password = new_password
                if user.save():
                    info = Success

        self.render_json(info)

    @authenticated
    def put(self):
        data = self.get_data()
        user = self.current_user

        info = Fail
        if 'password' in data and 'old_password' in data and user.authenticate(data['old_password']):
            user.from_dict(data)
            if user.save():
                info = Success

        self.render_json(info)


class UploadHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        info = Fail
        if 'photo' in self.request.files:
            save_images(self.request.files['photo'])
            info = Success

        self.render_json(info)


class SendCodeHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        phone = self.get_argument('p')
        code = self.get_argument('code')
        user = User.query.get_by_phone(phone)
        
        info = Fail
        if phone and code and not user and sms_send(phone, {'code': code}, 1) > 0:
            info = Success

        self.render_json(info)
