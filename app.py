import logging
import os
import tornado.options
import tornado.ioloop
import tornado.web as web
import tornado.websocket as websocket
import tornado.template as template
import tornado.httpserver
import tornado.options
import re
import json

room_to_ws={}

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        handlers = [
            (r"/static/(.*)", web.StaticFileHandler),
            (r"/room/(.*)", Chatroom),
            (r"/websocket", EchoWebSocket),
            ]

        tornado.web.Application.__init__(self, handlers, **settings)

class Chatroom(web.RequestHandler):
    def get(self,room_name):
        self.render("chatroom.html",room_name=room_name)

class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        #clients.append(self)
        room_name = self.get_argument('room',default = 'default_room')
        room_to_ws.setdefault(room_name,[]).append(self)

        logging.info(room_name)

    def on_message(self, message):
        logging.info('on_message')

        m = json.loads(message)
        room_name = m['room']
        msg = m['msg']
        logging.info(msg)

        for c in room_to_ws[room_name]:
            try:
                c.write_message(msg)
            except:
                logging.info('websocket write error')


    def on_close(self):
        pass
        #if self in clients:
        #    clients.remove(self)

if __name__ == "__main__":
    tornado.options.define('port', default=8888, help='port', metavar='p')
    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
