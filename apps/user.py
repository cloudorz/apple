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
            self.render_json(info)
        else:
            self.set_status(404)
            self.render_json(self.message("The user is not exsited."))

    @availabelclient
    def post(self, phn):
        user = User()

        data = self.get_data()
        data['avatar'] = 'i/%s.jpg' % data['phone'] 
        user.from_dict(data)

        if user.save():
            self.set_status(201)
            self.set_header('Location', "http://%s%s" % (self.request.host, self.reverse_url('loud', user.phone)))
            msg = self.message("Created Success.")
        else:
            self.set_status(400)
            msg = self.message("name,phone,password field are required.")
        
        self.render_json(msg)

    @authenticated
    @admin('phn', 'user')
    def put(self, user):
        ''' The User object can't modify phone
        '''
        data = self.get_data()
        user.from_dict(data)
        user.save()

        self.render_json(self.message("Modfied Success."))

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
        
        self.render_json(self.message("Delete Success."))

    def get_recipient(self, phn):
        return User.query.get_by_phone(phn)


class AuthHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        new_info = self.get_data()
        if 'phone' in new_info and 'password' in new_info:
            user = User.query.get_by_phone(new_info['phone'])
            if user and user.authenticate(new_info['password']):
                user.token = uuid.uuid5(uuid.NAMESPACE_URL, "%s%s" % (user.phone,
                    datetime.datetime.now())).hex
                info = user.user_to_dict_by_auth() # must before save
                user.save()

                self.render_json(info) 
                return 
            else:
                self.set_status(406)
                msg = self.message("Password or phone is not correct.")
        else:
            self.set_status(400)
            msg = self.message("phone, password field required.")

        self.render_json(msg)


class PasswordHandler(BaseRequestHandler):

    @authenticated
    @admin('phn', 'user')
    def get(self, user):
        pw = self.get_argument('pw')
        print 'fuck here 3', pw

        if user.authenticate(pw):
            print 'fuck here 1'
            msg = self.message("valid password for %s" % user.phone)
        else:
            print 'fuck here 2'
            self.set_status(406)
            msg = self.message("Password or name is not correct.")

        self.render_json(msg)

    @availabelclient
    def post(self, phn):

        user = User.query.get_by_phone(phn)
        if user:
            new_password = generate_password()

            if sms_send(user.phone, {'name': user.name, 'password': new_password}, 2) > 0:
                user.password = new_password
                user.save()
            msg = self.message("Message be sent.")
        else:
            self.set_status(404)
            msg = self.message("The user is not exsited.")

        self.render_json(msg)

    @authenticated
    @admin('phn', 'user')
    def put(self, user):

        data = self.get_data()

        if 'password' in data and 'old_password' in data:
            if  user.authenticate(data['old_password']):
                user.from_dict(data)
                user.save()
                msg = "Modified Success."
            else:
                self.set_status(406)
                msg = "The old password is not correct."
        else:
            self.set_status(400)
            msg = "password, old_password are reqeuired."

        self.render_json(msg)

    def get_recipient(self, phn):
        return User.query.get_by_phone(phn)


class UploadHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        if 'photo' in self.request.files:
            save_images(self.request.files['photo'])
            msg = self.message("Upload Success.")
        else:
            self.set_status(400)
            msg = self.message("photo field is requierd.")

        self.render_json(msg)


class SendCodeHandler(BaseRequestHandler):

    @availabelclient
    def post(self):
        data = self.get_data()
        
        if 'phone' in data and 'code' in data:
            user = User.query.get_by_phone(data['phone'])
            if not user:
                sms_send(data['phone'], {'code': data['code']}, 1)
                msg = "Message be sent."
            else:
                self.set_status(409)
                msg = "The user is already existed."
        else:
            self.set_status(400)
            msg = "phone, code fields are required."

        self.render_json(msg)
