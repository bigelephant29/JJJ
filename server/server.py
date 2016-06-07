#!/usr/bin/env/ python
import os
from tornado import web, ioloop, websocket
from tornado.options import define, options
import json
#import urllib2
from random import randint

import time
import _thread
import threading

define("ip", default="your.ip")
define("port", default=8888)


class User:
    def __init__(self, id, socket, thread, y, x):
        self.id = id
        self.socket = socket
        self.thread = thread
        self.position = [y, x]


#manage user
class Map(object):
    users = {}
    id_list = []
    map = []
    belong = []
    user_count = 0
    
    @classmethod
    def add_user(cls, id, websocket, thread):
        cls.users[id] = User(id, websocket, thread, randint(0, 44), randint(0, 89))
        cls.belong[cls.users[id].position[0]][cls.users[id].position[1]] = id
        #cls.users[id] = {'socket': websocket, 'thread': thread, 'position': [randint(0, 44), randint(0, 89)]}
        #cls.belong[cls.users[id]['position'][0]][cls.users[id]['position'[1]]] = id
        
        cls.id_list.append(id)
        cls.user_count += 1
        return id
    
    
    @classmethod
    def remove_user(cls, id):
        del cls.users[id]
        cls.id_list.remove(id)
        cls.user_count -= 1

    @classmethod
    def generate(cls):
        for i in range(45):
            tmp = []
            tmp2 = []
            for j in range(90):
                tmp.append(randint(0, 3))
                tmp2.append(-1)
            cls.map.append(tmp)
            cls.belong.append(tmp2)

    @classmethod
    def move(cls, id, dir):
        if(direction == 'r'):
            cls.users[id].position[1] += 1
        elif(direction == 'l'):
            cls.users[id].position[1] -= 1
        elif(direction == 'u'):
            cls.users[id].position[0] += 1
        elif(direction == 'd'):
            cls.users[id].position[0] -= 1
        elif(direction == 'h'):
            pass
        else:
            print("ERROR:Bad movement")

        cls.belong[cls.users[id].position[0]][cls.users[id].position[1]] = id

    @classmethod
    def checkMoveIntegraty(cls, id, direction):
        position = [cls.users[id].position[0], cls.users[id].position[1]]
        if(direction == 'r'):
            position[1] += 1
        elif(direction == 'l'):
            position[1] -= 1
        elif(direction == 'u'):
            position[0] += 1
        elif(direction == 'd'):
            position[0] -= 1
        elif(direction == 'h'):
            pass
        else:
            print("ERROR:Bad direction")

        #To Do: check if rock == 3
        if(position[0] < 45 and position[0] >= 0 and position[1] < 90 and position[1] >= 0 and map[position[0]][position[1]] != 3):
            return True
        else:
            return False

###########thread for user parsing############

#To do: connect with parser

exitFlag = 0;

class userThread(threading.Thread):
    def __init__(self, id):
        self.id = id
        self.command = []
        self.code = ""
        self.direction = 'h'
        self.ready = True
    
    def run(self):
        while not exitFlag:
            if(len(self.command) == 0):
                continue

            isCompute = False
            isChange = False
            while (len(self.command) != 0):
                cmd = self.command.pop()
                if(cmd == "compute"):
                    isCompute = True
                elif(cmd == "change"):
                    isChange = True
            
            if isCompute:
                '''interprete
                dir = interpretor.compute()
                '''
                if Map.checkMoveIntegraty(self.id, dir):
                    self.direction = dir
                else:
                    self.direction = 'h'
                
                Map.move(self.id, self.direction)
                self.ready = True

            if isChange:
                '''change code
                interpretor.change(self.code)
                '''
                print("Code changed!!")
    

    def computeAction(self):
        self.ready = False
        self.command.append("compute")

    def getAction(self):
        while not self.ready:
            pass
        return self.direction

    def changeCode(self, code):
        self.code = code
        self.command.append("change")
        
###########################################

# render UI
class UI(web.RequestHandler):
    def get(self):
        self.render("index.html")

# Interacte with client using websockethandler
class Socket(websocket.WebSocketHandler):
    id = -1
    def open(self):
        # save websocket if connection constructed
        if(Map.user_count > 4):
            print("user number exceeded, connection closing...")
            self.close()
        
        self.id = randint(0, 10000)
        thread = userThread(self.id)
        Map.add_user(id, self, thread)
        
        thread.start()
                
        d = {"map": Map.map, "position": [Map.users[self.id].position[0], Map.users[self.id].position[1]]}
        self.write_message(d)
        print (str(self.id) + ' [x] connected.')
    
    def on_close(self):
        # remove websocket of connection closed
        
        Map.remove_user(id)
        #To do: join thread
        
        print (str(self.id) + ' [x] disconnected.')
    
    def on_message(self, message):
        #To do:receive new code, done
        
        d = json.loads(message)
        print (d)
        
        Map.users[self.id].thread.changeCode(d['code'])
        
        '''
        for user in Map.users:
            Map.users[user].socket.write_message(message)
        '''
        print (str(self.id) + ' [x] send message.')

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

############ game main thread ###############
def clock(delay):
    count = 30
    isPrepare = True
    while True:
        if(Map.user_count > 4):
            continue
    
        time.sleep(delay)
        count -= 1
        if(count > 0):
            print (count)
            continue
        
        
        action = {}
        #tell user thread to compute
        for user in Map.users:
            Map.users[user].thread.computeAction()

        #get computed action
        for user in Map.users:
            action[user] = Map.users[user].thread.getAction()

        message = {}
        #check if occupy
        for user in Map.users:
            if(Map.belong[Map.users[user].position[0]][Map.users[user].position[1]] == user):
                message[user] = {'action': action[user], 'isOccupy': True}
            else:
                message[user] = {'action': action[user], 'isOccupy': False}

        for user in Map.users:
            Map.users[user].socket.write_message(message)

#To do: game over, calculate score and exit


        
#############################################
def main():
    Map.generate()
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    _thread.start_new_thread(clock, (1, ))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()




