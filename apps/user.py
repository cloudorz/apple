# coding: utf-8

import uuid, datetime, re

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.state import InstanceState

from tornado.web import HTTPError

from apps import BaseRequestHandler
from apps.models import User, Loud
from utils.decorator import authenticated, availabelclient, admin, owner
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
            raise HTTPError(404)

        self.render_json(info)

    @availabelclient
    def post(self, phn):
        user = User()
        data = self.get_data()
        data['avatar'] = 'i/%s.jpg' % data['phone'] 
        user.from_dict(data)

        self.render_json(user.save() and Success or Fail)

    @authenticated
    @admin('phn', 'user')
    def put(self, user):
        ''' The User object can't modify phone
        '''
        data = self.get_data()
        user.from_dict(data)

        self.render_json(user.save() and Success or Fail)

    @authenticated
    @admin('phn', 'user')
    def delete(self, user):
        # PS: delete all relation data user_id = 0

        if user.owner_by(self.current_user):
            self.db.delete(user) 
            self.db.commit()
        else:
            user.block = True
            user.save()
        
        self.render_json(Success)

    def get_recipient(self, phn):
        return User.query.get_by_phone(phn)


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
    @admin('phn', 'user')
    def get(self, user):
        pw = self.get_argument('pw')

        info = Fail
        if user.authenticate(pw):
            info = Success

        self.render_json(info)

    @availabelclient
    def post(self, phn):
        info = Fail
        user = User.query.get_by_phone(phn)
        if user:
            new_password = generate_password()

            if sms_send(user.phone, {'name': user.name, 'password': new_password}, 2) > 0:
                user.password = new_password
                if user.save():
                    info = Success

        self.render_json(info)

    @authenticated
    @admin('phn', 'user')
    def put(self, user):
        data = self.get_data()

        info = Fail
        if 'password' in data and 'old_password' in data and user.authenticate(data['old_password']):
            user.from_dict(data)
            if user.save():
                info = Success

        self.render_json(info)

    def get_recipient(self, phn):
        return User.query.get_by_phone(phn)


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
        data = self.get_data()
        user = User.query.get_by_phone(data['phone'])

        if user: raise HTTPError(409)
        
        info = Fail
        if data['phone'] and data['code'] and sms_send(data['phone'], {'code': data['code']}, 1) > 0:
            info = Success

        self.render_json(info)
