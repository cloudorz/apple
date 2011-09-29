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
from utils.mkthings import generate_password, QDict

class UserHandler(BaseRequestHandler):

    @authenticated
    def get(self, phn):
        if phn:
            user = User.query.get_by_phone(phn)

            if user:
                info = user.user_to_dict(self.current_user)
                self.render_json(info)
            else:
                self.set_status(404)
                self.render_json(self.message("The user is not exsited."))
        else:
            q = QDict(
                    q=self.get_argument('q', ""),
                    sort=self.get_argument('qs'),
                    start=int(self.get_argument('st')),
                    num=int(self.get_argument('qn')),
                    )

            query_users = User.query.get_users()

            if q.q:
                query_users = query_users.filter(User.name.like('%'+q.q+'%'))

            # composite the results collection
            total = query_users.count()
            query_dict = {
                    'q': q.q,
                    'qs': q.sort,
                    'st': q.start,
                    'qn': q.num,
                    }

            user_collection = {
                    'users': [e.user_to_dict(self.current_user) for e in query_users.order_by(q.sort).limit(q.num).offset(q.start)],
                    'total': total,
                    'link': self.full_uri(query_dict),
                    }

            if q.start + q.num < total:
                query_dict['st'] = q.start + q.num
                user_collection['next'] = self.full_uri(query_dict)

            if q.start > 0:
                query_dict['st'] = max(q.start - q.num, 0)
                user_collection['prev'] = self.full_uri(query_dict)

            return self.render_json(user_collection)

    @availabelclient
    def post(self, phn):
        user = User()

        data = self.get_data()
        data['avatar'] = 'i/%s.jpg' % data['phone'] 
        user.from_dict(data)

        if user.save():
            self.set_status(201)
            self.set_header('Location', user.get_link())
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

        if 'phone' in data:
            self.set_status(403)
            msg = self.message("phone can't be changed.")
        else:
            if 'password' in data and not ('old_password' in data and user.authenticate(data['old_password'])):
                self.set_status(412)
                msg = self.message("Incorrect password.")
            else:
                user.from_dict(data)
                user.save()
                msg = self.message("Modfied Success.")

        self.render_json(msg)

    @authenticated
    @admin('phn', 'user')
    def delete(self, user):
        # PS: delete all relation data user_id = 0

        if user.owner_by(self.current_user):
            pw = self.get_argument('pw')
            if user.authenticate(pw):
                self.db.delete(user) 
                self.db.commit()
                msg = self.message("Delete Success.")
            else:
                self.set_status(412)
                msg = self.message("Password is not correct.")
        else:
            user.block = True
            user.save()
            msg = self.message("Block Success.")
        
        self.render_json(msg)

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
                msg = self.message("Modified Success.")
            else:
                self.set_status(406)
                msg = self.message("The old password is not correct.")
        else:
            self.set_status(400)
            msg = self.message("password, old_password are reqeuired.")

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
                msg = self.message("Message be sent.")
            else:
                self.set_status(409)
                msg = self.message("The user is already existed.")
        else:
            self.set_status(400)
            msg = self.message("phone, code fields are required.")

        self.render_json(msg)
