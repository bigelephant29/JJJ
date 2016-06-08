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

import sys
sys.path.insert(0, '../interpreter')
import JJJInterpreter as interpreter

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
    mymap = []
    belong = []
    user_count = 0
    
    
    @classmethod
    def add_user(cls, id, websocket, thread):
        cls.users[id] = User(id, websocket, thread, randint(15, 29), randint(30, 59))
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
            cls.mymap.append(tmp)
            cls.belong.append(tmp2)

    @classmethod
    def move(cls, id, dir):
        if(dir == 'r'):
            cls.users[id].position[1] += 1
        elif(dir == 'l'):
            cls.users[id].position[1] -= 1
        elif(dir == 'u'):
            cls.users[id].position[0] -= 1
        elif(dir == 'd'):
            cls.users[id].position[0] += 1
        elif(dir == 'h'):
            pass
        else:
            print("ERROR:Bad movement")

        cls.belong[cls.users[id].position[0]][cls.users[id].position[1]] = id

    @classmethod
    def checkMoveIntegraty(cls, id, direction):
        position = cls.users[id].position[:]
        #position = [cls.users[id].position[0], cls.users[id].position[1]]
        if(direction == 'r'):
            position[1] += 1
        elif(direction == 'l'):
            position[1] -= 1
        elif(direction == 'u'):
            position[0] -= 1
        elif(direction == 'd'):
            position[0] += 1
        elif(direction == 'h'):
            pass
        else:
            print("ERROR:Bad direction")
        
        #To Do: check if rock == 3
        if(position[0] < 45 and position[0] >= 0 and position[1] < 90 and position[1] >= 0 and cls.mymap[position[0]][position[1]] != 3):
            return True
        else:
            return False

    @classmethod
    def scoring():
        score = {}
        for user in id_list:
            score[user] = 0

        for row in belong:
            for id in row:
                if id == -1:
                    continue
                score[id] += 1

        return score


########## thread for user parsing ##########
# Each user run a thread, looping to check  #
# if there is any command in command list   #
# and execute. Main thread call the member  #
# function to append command to the command #
# list, awake user thread to excute the     #
# command.                                  #
#############################################

#To do: connect with parser, done

exitFlag = 0;

class userThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.command = []
        self.code = ""
        self.direction = 'h'
        self.ready = True
    
    def run(self):
        inte = interpreter.JJJInterpreter()
        cnt = 0
        while not exitFlag:
            cnt += 1
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
                        
            if isChange:
                #change code interprete by inte
                inte.sendCommand(self.code)
        
                #print("Code changed!! " + str(cnt))

            if isCompute:
                #compute user movement
                dir = inte.getCommand()
        
                if dir == inte.CommandType.up:
                    dir = 'u'
                if dir == inte.CommandType.down:
                    dir = 'd'
                if dir == inte.CommandType.left:
                    dir = 'l'
                if dir == inte.CommandType.right:
                    dir = 'r'
                if dir == None:
                    dir = 'h'
                
                if Map.checkMoveIntegraty(self.id, dir):
                    self.direction = dir
                else:
                    self.direction = 'h'
                
                Map.move(self.id, self.direction)
                self.ready = True

                #print("Action computed!! " + str(cnt))

               

    def computeAction(self):
        self.ready = False
        self.command.append("compute")
        print("compute")

    def getAction(self):
        while not self.ready:
            pass
        return self.direction

    def changeCode(self, code):
        self.code = code
        self.command.append("change")
        print("change")
        
###########################################

# render UI
class UI(web.RequestHandler):
    def get(self):
        self.render("index.html")

# Interacte with client using websockethandler
class Socket(websocket.WebSocketHandler):
    id = -1
    def open(self):
        print("haha")
        # save websocket if connection constructed
        if(Map.user_count >= 1):
            print("user number exceeded, connection closing...")
            self.close()
        
        
        self.id = Map.user_count
        thread = userThread(self.id)
        Map.add_user(self.id, self, thread)
        
        thread.start()
                
                #d = {"myname": self.id, "map": Map.map, "position": [Map.users[self.id].position[0], Map.users[self.id].position[1]]}
        d = {"map": Map.mymap}
        self.write_message(d)
        d = {"myname": self.id}
        self.write_message(d)
        d = {"position": [Map.users[self.id].position[0], Map.users[self.id].position[1]]}
        self.write_message(d)
        print(d["position"])
        #print(d['myname'])
        print (str(self.id) + ' [x] connected. User number: ' + str(Map.user_count))
    
    def on_close(self):
        # remove websocket of connection closed
        
        Map.remove_user(self.id)
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

########## game main thread ##########
# Maintain the integraty of the game #
# flow. Call user thread and get the #
# action of user. Send information   #
# to client.                         #
######################################
def clock(delay):
    
    while Map.user_count < 1:
        pass
    
    print("user preparing...")

    count = 5
    short_command = "up\ndown\nleft\nright"

    while count > 0:
        print (count)
        time.sleep(delay)
        count -= 1

    print("game start!!")
    userinit = []
    for user in Map.id_list:
        userinit.append([Map.users[user].position[0], Map.users[user].position[1]])

    for user in Map.users:
        Map.users[user].socket.write_message({'username': Map.id_list})
        Map.users[user].socket.write_message({'userinit': userinit})
        Map.users[user].thread.changeCode(short_command)

    count = 120
    while count > 0:
        action = {}
        #tell user thread to compute
        for user in Map.users:
            Map.users[user].thread.computeAction()

        #get computed action
        for user in Map.users:
            action[user] = Map.users[user].thread.getAction()
            print(str(user) + " " + action[user])
            print(Map.users[user].position)
            print("up: " + str(Map.mymap[Map.users[user].position[0] - 1][Map.users[user].position[1]]))
            print("down: " + str(Map.mymap[Map.users[user].position[0] + 1][Map.users[user].position[1]]))
            print("left: " + str(Map.mymap[Map.users[user].position[0]][Map.users[user].position[1] - 1]))
            print("right: " + str(Map.mymap[Map.users[user].position[0]][Map.users[user].position[1] + 1]))

        message = {}
        #check if occupy
        for user in Map.users:
            if(Map.belong[Map.users[user].position[0]][Map.users[user].position[1]] == user):
                message[user] = {'action': action[user], 'isOccupy': True}
            else:
                message[user] = {'action': action[user], 'isOccupy': False}

        #send user information
        for user in Map.users:
            Map.users[user].socket.write_message({'move': message})

        time.sleep(delay)

    #To do: game over, calculate score and exit
    score = Map.scoring()
    for user in Map.users:
        Map.users[user].socket.write_message({'score': score})

    exitFlag = 1
    for user in Map.users:
        Map.users[user].thread.join()


######################################
def main():
    Map.generate()
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    _thread.start_new_thread(clock, (1, ))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()




