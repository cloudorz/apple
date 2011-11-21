# coding: utf-8

import httplib, datetime

import tornado.web
import ooredis

from tornado.web import HTTPError
from tornado.options import options
from tornado.httputil import url_concat
from tornado.escape import url_unescape

from utils.escape import json_encode, json_decode
from utils.mkthings import QDict
from apps.models import User

class BaseRequestHandler(tornado.web.RequestHandler):
    """the base RequestHandler for All."""

    @property
    def db(self):
        return self.application.db_session

    # json pickle data methods
    def json(self, data):
        dthandler = lambda obj: obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else obj
        return json_encode(data, default=dthandler)

    # decode json picle data 
    def dejson(self, data):
        return json_decode(data)

    def get_data(self):
        ''' parse the data from request body
        now, only convert json data to python type
        '''
        # the content type is not "application/json"
        if not self.is_pretty:
            raise HTTPError(415)

        try:
            data = self.dejson(self.request.body);
        except (ValueError, TypeError), e:
            raise HTTPError(415) # the data is not the right josn format

        return data

    @property
    def is_pretty(self):
        return self.request.headers.get('Content-Type', '').split(';').pop(0).strip().lower() == 'application/json'

    def get_error_html(self, status_code, **kwargs):
        ''' all error response where json data {'code': ..., 'msg': ...}
        '''
        return self.json({'code': status_code, 'msg': httplib.responses[status_code]})

    # render data string for response
    def render_json(self, data, **kwargs):
        self.set_header('Content-Type', 'Application/json; charset=UTF-8')
        self.write(self.json(data))

    def get_current_user(self):
        tk = self.get_argument('tk')
        key = 'users:%s' % tk

        if self.is_available_client():
            user_dict = ooredis.Dict(key)
            if not user_dict:
                user = User.query.get_by_token(tk)
                if user:
                    user_dict.update(user.user2dict4redis())
                    #user_dict.expire(3600)

            if user_dict:
                return QDict(dict(user_dict))

        return None

    def is_available_client(self):
        app_key = self.get_argument('ak')
        return app_key == options.app_key

    def message(self, msg):
        return {'msg': msg}

    def full_uri(self, query_dict=None):
        #return url_unescape(url_concat("%s%s" % (options.site_uri, self.request.path), query_dict))
        return url_concat("%s%s" % (options.site_uri, self.request.path), query_dict)
