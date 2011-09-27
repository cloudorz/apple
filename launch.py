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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from apps.loud import LoudHandler, LoudSearchHandler, LoudManageHandler
from apps.user import UserHandler, AuthHandler, PasswordHandler, UploadHandler, SendCodeHandler
from utils.coredb import sql_db

# server
define('port', default=8888, help="run on the given port", type=int)

# database
define('db_uri', default="mysql://root:123@localhost/apple?charset=utf8", type=str, help="connect to mysql")

# avatar dir  path
define('path', default="/data/web/static/i/", type=str, help="recommend default one")

# app key
define("app_name", default="apple", help="app name")
define("app_key", default="12345678", help="app key")
define("app_secret", default="jkafldjaklfjda978-=-^**&", help="app secret")


# main logic
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                (r'^/l/(?P<lid>\d+|)$', LoudHandler, {}, 'loud'),
                (r'^/l/list$', LoudSearchHandler),
                (r'^/l/dels$', LoudManageHandler),
                (r'^/u/(?P<phn>\d{11}|)$', UserHandler, {}, 'user'),
                (r"^/u/(?P<phn>\d{11}|)/passwd$", PasswordHandler),
                (r"^/auth$", AuthHandler),
                (r"^/code$", SendCodeHandler),
                (r"^/upload$", UploadHandler),
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
