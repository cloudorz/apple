# coding: utf-8

import httplib, datetime

import tornado.web
from utils.escape import json_encode, json_decode

from apps.models import User

class BaseRequestHandler(tornado.web.RequestHandler):
    """the base RequestHandler for All."""

    @property
    def db(self):
        return self.application.db_session

    # json pickle data methods
    def json(self, data):
        dthandler = lambda obj: str(obj) if isinstance(obj, (datetime.datetime, datetime.date)) else obj
        return json_encode(data, default=dthandler)

    # decode json picle data 
    def dejson(self, data):
        # FIXME other exception data
        return json_decode(data)

    def get_data(self):
        ''' parse the data from request body
        now, only convert json data to python type
        '''
        # the content type is not "application/json"
        if not self.is_pretty:
            data =  None

        try:
            data = self.dejson(self.request.body);
        except ValueError:
            # the data is not the right josn format
            data = None

        # FIXME maybe data validation
        return data

    @property
    def is_pretty(self):
        return self.request.headers.get('Content-Type', '').strip().lower() == 'application/json'

    def get_error_html(self, status_code, **kwargs):
        ''' all error response where json data {'code': ..., 'msg': ...}
        '''
        return self.json({'code': status_code, 'msg': httplib.responses[status_code]})

    # render data string for response
    def render_json(self, data, **kwargs):
        self.set_header('Content-Type', 'Application/json')
        self.write(self.json(data))

    def get_current_user(self):
        tk = self.get_argument('tk')
        app = self.get_argument('app')
        # validate the app key
        return User.query.get_by_token(tk)
