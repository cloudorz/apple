# coding: utf-8
'''
'''

import os.path

import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop

from tornado.options import define, options

define('port', default=8888, help="run on the given port", type=int)
#define("mysql_host", default="127.0.0.1:3306", help="blog database host")
#define("mysql_database", default="blog", help="blog database name")
#define("mysql_user", default="blog", help="blog database user")
#define("mysql_password", default="blog", help="blog database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                #(r"/login", AuthLoginHandler),
                #(r"/logout", AuthLogoutHandler),
                # normal ye mian
                (r"/", pages.HomeHandler),
                # registraction
                ]
        settings = dict(
                site_name=u"Help anyone",
                static_path=os.path.join(os.path.dirname(__file__), 'static'),
                template_path=os.path.join(os.path.dirname(__file__), 'templates'),
                xsrf_cookies=True,
                cookie_secret='c8f48f9777f411e09fcd109add59054a',
                login_url='/login',
                debug=True,
                )
        super(Application, self).__init__(handlers, **settings)
        # TODO init sqlalchemy connection
        #self.rs= None

def main():
    tornado.options.parse_command_line()
    # ssl_options TODO
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
