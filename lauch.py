# coding: utf-8
'''
'''

import tornado.web
import tornado.options
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
#define("mysql_host", default="127.0.0.1:3306", help="blog database host")
#define("mysql_database", default="blog", help="blog database name")
#define("mysql_user", default="blog", help="blog database user")
#define("mysql_password", default="blog", help="blog database password")


class AppleApplicaiton(tornado.web.Applicaiton):
    def __init__(self):
        handlers = [
                (r"/login", AuthLoginHandler),
                (r"/logout", AuthLogoutHandler),
                ]
        settings = dict(
                bolg_title=u"One Paper",
                static_path=os.path.join(os.path.dirname(__file__), 'static'),
                template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                xsrf_cookies=True,
                cookie_secret='c8f48f9777f411e09fcd109add59054a',
                login_url='/login',
                )
        super(Applicaiton, self).__init__(handers, **settings)
        # TODO init sqlalchemy connection
        self.rs= None
