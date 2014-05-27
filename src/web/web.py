#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os.path
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

from handlers.home import HomeHandler
from handlers.more import MoreHandler
from handlers.about import AboutHandler
from handlers.search import SearchLucHandler

define("port", default=8080, help="run on the given port", type=int)

reload(sys)
sys.setdefaultencoding('utf-8')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/more/([a-z0-9A-Z\_\-]+)/([a-z]+)", MoreHandler),
            (r"/about", AboutHandler),
            (r"/search_luc", SearchLucHandler),
            ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret="18oETzKXQAGaYdkL5gEmGEJJFuYh7ENnpTXdTP1o/Vo=",
            login_url="/login",
            autoescape=None,
            )
        tornado.web.Application.__init__(self, handlers, **settings)

class WebApp(object):
    def __init__(self):
        pass
    def run(self):
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()        

if __name__ == "__main__":
    WebApp().run()
