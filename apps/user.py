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
        print dir(user)
        print type(user.louds)

        #print vars(user)
        for e in vars(user):
            if isinstance(e, InstanceState):
                print dir(e)
                print vars(e)
        print user.louds
        # TODO ower test
        owner = False
        if owner:
            # user get the (content longitude latitude grade created phone name avatar last_longitude last_atitude
            # loud_num is_admin distance updated created)
            info = self.owner_info(user)
        else:
            # non self get the (phone, name, avatar, last_longitude, last_atitude, updated)
            info = self.other_info(user)

        self.render_json(info)

    def post(self, phn):
        # TODO #3 create user 
        data = self.get_data()
        self.render_json("doing")

    def put(self, phn):
        # FIXME if is owner
        data = self.get_data()
        user = User.query.get_by_phone(phn)

        # TODO #3 create the update key=value strings
        self.render_json(data)

    def delete(self, phn):
        # FIXME if is owner
        user = User.query.get_by_phone(phn)
        # delete all relation data
        msg = {'status': 'fail'}
        if user:
            self.db.delete(user)
            msg = {'status': 'success'}
        # delete user data 
        self.render_json(msg)

    # data mainiupulate 
    def owner_info(self, data):
        return 'ok'

    def other_info(self, data):
        return 'ok'

class AuthHandler(BaseRequestHandler):
    pass
