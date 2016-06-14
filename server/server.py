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


#To do: map randomize, done
#       bfs
#       config, done
#       code rejection, done
#       other rule
#       init on rock, done
#       user left
#       thread join done


MAX_USER = 2
GAME_TIME = 300
CLOCK_DELAY = 0.5
PREPARE_TIME = 5

GRASS1_PROB = [0, 1, 2]
GRASS2_PROB = [3, 4, 5]
FLOWER_PROB = [6, 7, 8]
ROCK_PROB = [9]
RANDOM_SIZE = len(GRASS1_PROB) + len(GRASS2_PROB) + len(FLOWER_PROB) + len(ROCK_PROB) - 1

isStart = False


class User:
    def __init__(self, id, socket, thread, y, x):
        self.id = id
        self.socket = socket
        self.thread = thread
        self.position = [y, x]
        self.online = True


#manage user
class Map(object):
    users = {}
    id_list = []
    mymap = []
    belong = []
    user_count = 0
    
    
    @classmethod
    def add_user(cls, id, websocket, thread):
        y = randint(15, 29)
        x = randint(30, 59)
        while cls.mymap[y][x] == 3:
            y = randint(15, 29)
            x = randint(30, 59)
        cls.users[id] = User(id, websocket, thread, y, x)
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
        print(GRASS1_PROB)
        print(GRASS2_PROB)
        print(FLOWER_PROB)
        print(ROCK_PROB)
        for i in range(45):
            tmp = []
            tmp2 = []
            

            for j in range(90):
                randnum = randint(0, RANDOM_SIZE)
                if randnum in GRASS1_PROB:
                    tmp.append(0)
                elif randnum in GRASS2_PROB:
                    tmp.append(1)
                elif randnum in FLOWER_PROB:
                    tmp.append(2)
                elif randnum in ROCK_PROB:
                    tmp.append(3)
                
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
    def scoring(self):
        score = {}
        for user in self.id_list:
            score[user] = 0

        for row in self.belong:
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


class userThread(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.command = []
        self.code = ""
        self.direction = 'h'
        self.ready = True
        self.exit = False
    
    def run(self):
        inte = interpreter.JJJInterpreter()
        cnt = 0
        while not self.exit:
            cnt += 1
            #print(cnt)
            if(len(self.command) == 0):
                continue

            isCompute = False
            isChange = False
            while (len(self.command) != 0):
                cmd = self.command.pop()
                if(cmd == "compute"):
                    isCompute = True
                    #print("hahahas")
                elif(cmd == "change"):
                    isChange = True
                        
            if isChange:
                #change code interprete by inte
                errorline = inte.sendCommand(self.code)
                if(errorline >= 0):
                    print("Invalid code: line " + str(errorline))
                    Map.users[self.id].socket.write_message({'error': errorline})
                    
                #print("Code changed!! " + str(cnt))
            

            if isCompute:
                #compute user movement
                #print("before")
                dir = inte.getCommand()
                #print("after")
                if dir == inte.CommandType.up:
                    dir = 'u'
                if dir == inte.CommandType.down:
                    dir = 'd'
                if dir == inte.CommandType.left:
                    dir = 'l'
                if dir == inte.CommandType.right:
                    dir = 'r'
                if dir == None:
                    #print("hehe")
                    self.ready = True
                    continue
                    #dir = 'h'
                
                #print("hahaha")
                self.direction = dir
                if Map.checkMoveIntegraty(self.id, dir):
                    Map.move(self.id, self.direction)
                    
    
                self.ready = True
                '''
                if Map.checkMoveIntegraty(self.id, dir):
                    self.direction = dir
                else:
                    self.direction = 'h'
                
                Map.move(self.id, self.direction)
                self.ready = True
                '''
                #print("Action computed!! " + str(cnt))

               

    def computeAction(self):
        self.ready = False
        self.command.append("compute")
        #print("compute")

    def getAction(self):
        if not self.ready:
            #print("kerker")
            return None
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
        #print("haha")
        # save websocket if connection constructed
        if(Map.user_count >= MAX_USER):
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
        global isStart
        print(isStart)
        if isStart:
            Map.users[self.id].online = False
        else:
            print("user left during game")
            Map.users[self.id].thread.exit = True
            Map.users[self.id].thread.join()
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
    
    while Map.user_count < MAX_USER:
        pass
    
    print("user preparing...")
    global isStart
    isStart = True
    print(isStart)
    count = PREPARE_TIME

    while count > 0:
        print (count)
        time.sleep(1)
        count -= 1

    print("game start!!")
    userinit = []
    for user in Map.id_list:
        userinit.append([Map.users[user].position[0], Map.users[user].position[1]])

    for user in Map.users:
        if(Map.users[user].online):
            Map.users[user].socket.write_message({'username': Map.id_list})
            Map.users[user].socket.write_message({'userinit': userinit})


    count = 0

    t0 = time.time()
    while count < GAME_TIME:
        count += delay
        action = {}
        #tell user thread to compute
        for user in Map.users:
            Map.users[user].thread.computeAction()

        #get computed action

        ids = Map.id_list[:]
        #print(ids)

        #print(str(count - (time.time() - t0)))
        while len(ids) != 0 and time.time() - t0 < count:
            id = ids.pop(0)
            action[id] = Map.users[id].thread.getAction()
            if action[id] == None:
                ids.append(id)

        '''
        for user in Map.users:
            action[user] = Map.users[user].thread.getAction()
            print(str(user) + " " + action[user])
            
            print(Map.users[user].position)
            print("up: " + str(Map.mymap[Map.users[user].position[0] - 1][Map.users[user].position[1]]))
            print("down: " + str(Map.mymap[Map.users[user].position[0] + 1][Map.users[user].position[1]]))
            print("left: " + str(Map.mymap[Map.users[user].position[0]][Map.users[user].position[1] - 1]))
            print("right: " + str(Map.mymap[Map.users[user].position[0]][Map.users[user].position[1] + 1]))
            '''

        message = {}
        #check if occupy
        #print(action)
        for user in Map.users:
            if(action[user] == None):
                #print("haha")
                action[user] = 'h'
            if(Map.belong[Map.users[user].position[0]][Map.users[user].position[1]] == user):
                message[user] = {'position': Map.users[user].position[:],'direction': action[user], 'isOccupy': True}
            else:
                message[user] = {'position': Map.users[user].position[:],'direction': action[user], 'isOccupy': False}

        #send user information
        print(message)
        for user in Map.users:
            if(Map.users[user].online):
                Map.users[user].socket.write_message({'move': message})
        #print(str(time.time() - t0))
        remain = count - (time.time() - t0)
        if(remain > 0):
            time.sleep(remain)
            #count -= 1
        #print(str(time.time() - t0))
        #print("======================")

    #To do: game over, calculate score and exit
    score = Map.scoring()
    print(score)
    for user in Map.users:
        if(Map.users[user].online):
            Map.users[user].socket.write_message({'score': score})


    for user in Map.users:
        Map.users[user].thread.exit = True
        Map.users[user].thread.join()


######################################
def main():
    global isStart
    Map.generate()
    options.parse_command_line()
    app = Application()
    app.listen(options.port)
    _thread.start_new_thread(clock, (CLOCK_DELAY, ))
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()




