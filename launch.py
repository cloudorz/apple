# coding: utf-8
'''
'''

import os.path

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
define('site_uri', default="http://rest.whohelp.me", type=str, help="site uri")
define('static_uri', default="http://static.whohelp.me", type=str, help="static uri")

#args
define('er', default=6378137, type=float, help="the earth radius.")
define('cr', default=3000, type=float, help="the cycle radius.")

# database
define('db_uri', default="mysql://root:123@localhost/apple?charset=utf8", type=str, help="connect to mysql")

# avatar dir  path
define('path', default="/data/web/static/", type=str, help="recommend default one")

# app key
define("app_name", default="lebang", help="app name")
define("app_key", default="20111007001", help="app key")
define("app_secret", default="9e6306f58b705e44d585d61e500d884d", help="app secret")
define("token_secret", default="bc400ed500605c49a035eead0ee5ef41", help="token secret")


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
                cookie_secret='c8f48f9777f411e09fcd109add59054a',
                debug=True,
                )
        super(Application, self).__init__(handlers, **settings)

        # sqlalchemy session 'db'
        self.db_session = (scoped_session(sessionmaker(autoflush=True, bind=create_engine(options.db_uri))))()


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
