#!/usr/bin/env/ python
import os
from tornado import web, ioloop, websocket
from tornado.options import define, options
import json
import urllib2

define("ip", default="your.ip")
define("port", default=8888)

#manage user
class Map(object):
    users = []
    @classmethod
    def add_user(cls, websocket):
        cls.users.append(websocket)
    
    @classmethod
    def remove_user(cls, websocket):
        cls.users.remove(websocket)

# render UI
class UI(web.RequestHandler):
    def get(self):
        self.render("index.html")

# Interacte with client using websockethandler
class Socket(websocket.WebSocketHandler):
    def open(self):
        # save websocket if connection constructed
        print ' [x] connected.'
        Map.add_user(self)
        d = {map: [[1, 2, 3], [4, 5, 6]]}
        self.write_message(d)

    
    def on_close(self):
        # remove websocket of connection closed
        print ' [x] disconnected.'
        Map.remove_user(self)
    
    def on_message(self, message):
        # send message to other WebSocket if some one send a message
        print ' [x] send message.'
        d = json.loads(message)
        #print d.user + ': ' + d.msg_input
        print "haha"
        print d
        d = {map: [[1, 2, 3], [4, 5, 6]]}
        for user in Map.users:
            user.write_message(message)

# setting parameter
settings = dict(
                debug=True,
                autoreload=True,
                compiled_template_cache=False,
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                template_path=os.path.join(os.path.dirname(__file__), "templates")
                )

class Application(web.Application):
    def __init__(self):
        handlers = [
                    (r"/", UI),
                    (r"/socket", Socket)
                    ]
        web.Application.__init__(self, handlers, **settings)

def main():
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()