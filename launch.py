# coding: utf-8
'''
'''

import os.path
import redis

import tornado.web
import tornado.httpserver
import tornado.database
import tornado.options
import tornado.ioloop

from tornado.options import define, options
from tornado.web import url

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from apps.loud import LoudHandler, SearchLoudHandler, UpdatedLoudHandler
from apps.user import UserHandler, AuthHandler, ResetPasswordHandler, UploadHandler, SendCodeHandler
from utils.coredb import sql_db

# server
define('port', default=8888, help="run on the given port", type=int)

#URI
# P.S: FIXME set your args 
#
define('site_uri', default="<uri for your service>", type=str, help="site uri") 
define('static_uri', default="<uri for static files>", type=str, help="static uri")
define('geo_uri', default="<uri for parse the geo data>", type=str, help="locaiton and address parser uri")
define('sms_uri', default="http://utf8.sms.webchinese.cn/?Uid=<your-id>&Key=<your-key>&smsMob=%(phone)s&smsText=%(msg)s", type=str, help="sms servcie uri")

#args
define('er', default=6378137, type=float, help="the earth radius.")
define('cr', default=3000, type=float, help="the cycle radius.")

# database
define('db_uri', default="mysql://<mysql-user>:<mysql-passwd>@<mysql-host>/<db-name>?charset=utf8", type=str, help="connect to mysql")

# avatar dir  path
define('path', default="/path/to/your/static/", type=str, help="recommend default one")

# app key
define("app_name", default="lebang", help="app name")
define("app_key", default="<your app key>", help="app key")
define("app_secret", default="xxxxxxxxxxxxxxxxxx", help="app secret")
define("token_secret", default="xxxxxxxxxxxxxxxxxxxx", help="token secret")


# main logic
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                url(r'^/update$', UpdatedLoudHandler),
                url(r'^/s$', SearchLoudHandler),
                url(r'^/l/(?P<lid>\d+|)$', LoudHandler, name='loud'),
                url(r"^/auth$", AuthHandler),
                url(r'^/u/(?P<phn>\d{11}|)$', UserHandler, name='user'),
                url(r"^/upload$", UploadHandler),
                url(r"^/code$", SendCodeHandler),
                url(r"^/reset/(?P<phn>\d{11})$", ResetPasswordHandler),
                ]
        settings = dict(
                static_path=os.path.join(os.path.dirname(__file__), 'static'),
                xsrf_cookies=False,
                cookie_secret='cuf48f9777f411e12fcd109edd52054a',
                debug=False,
                )
        super(Application, self).__init__(handlers, **settings)

        # sqlalchemy session 'db'
        self.db_session = (scoped_session(sessionmaker(autoflush=True, bind=create_engine(options.db_uri))))()
        # redis connection
        self.redis = redis.Redis(host="localhost", port=6379, db=0)


def main():
    tornado.options.parse_command_line()
    # ssl_options TODO
    app = Application()

    # init the modual
    sql_db.init_app(app)

    # server 
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
