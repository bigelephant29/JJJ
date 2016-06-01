from enum import Enum
import queue

class JJJInterpreter:
     
    def __init__(self):
        self.isLabeled = 0
        self.commandList = []
        self.register = [-999, 0, 0, 0, 0]   
        self.buffQueue = queue.Queue()
        
    # Enum Class for command types
    class CommandType(Enum):
        noType = 0
        up = 1
        down = 2
        left = 3
        right = 4
        jump = 5
        label = 6
        assign = 7
        debug_print = 999
     
    # Function for parsing a single element (not a expression)
    def getElementValue(self, exp):
        # Case for self.register element
        if exp[0] == '$':
            if len(exp) != 2:
                return None
            if exp[1] not in ['1', '2', '3', '4']:
                return None
            return self.register[ord(exp[1]) - ord('0')]
        # Case for constant element
        try:
            val = int(exp)
        except ValueError:
            return None
        return val
        
    # Function for evaluating the value of a expression
    def parseRightExpr(self, exp):
        operatorList = ["+", "-", "*", "/"]
        operatorType = None
        operatorIndex = 0
        # Check if the expression contains an operator in operator list
        for i in operatorList:
            operatorIndex = exp.rfind(i)
            if operatorIndex != -1:
                operatorType = i
                break
        # Deal with the leading '-' for some constant expressions
        if operatorType == '-' and operatorIndex == 0:
            operatorType = None;
        # Case for constant expression
        if operatorType == None:
            return self.getElementValue(exp)
        # Case for non-constant expression
        expressionElement = exp.split(operatorType)
        val1 = self.getElementValue(expressionElement[0])
        val2 = self.getElementValue(expressionElement[1])
        if val1 == None or val2 == None:
            return None
        if operatorType == "+":
            return val1 + val2
        elif operatorType == "-":
            return val1 - val2
        elif operatorType == "*":
            return val1 * val2
        elif operatorType == "/":
            return val1 / val2
            
    # Function for sending command to interpreter, return 1 on success, 0 on fail
    def addCommand(self, cmd):
        # Remove spaces in command
        cmd = cmd.replace(" ", "")
        # Try to find "=" in command
        equalLocation = cmd.find("=")
        # equalLocation == -1  means the command is not a assignment
        if equalLocation == -1:
            # Command Types
            if cmd == "up":
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.up,));
            elif cmd == "down":
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.down,));
            elif cmd == "left":
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.left,));
            elif cmd == "right":
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.right,));
            elif cmd == "jump":
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.jump,));
            elif cmd == "label":
                print(len(self.commandList))
                # Set a label for jump
                if ( len(self.commandList) > 0 ):
                    del self.commandList[:]
                # Set labeled flag
                self.isLabeled = 1
            else:
                print ('[ERROR] Invalid Input: ', cmd)
                return 0
        else:
            # Assign/Operation Type
            nowCommand = (self.CommandType.assign, cmd)
            cmd = cmd.split('=')
            # print=$1 command is for debugging
            if cmd[0] == 'print':
                if len(cmd[1]) == 2 and cmd[1][0] == '$' and cmd[1][1] in ['1', '2', '3', '4']:
                    print ('value of ' + cmd[1] + ' = ' + str(self.register[ord(cmd[1][1])-ord('0')]))
            elif cmd[0][0] == '$':
                if cmd[0][1] in ['1', '2', '3', '4']:
                    # Parse the assignment
                    regNum = ord(cmd[0][1]) - ord('0')
                    expressionVal = self.parseRightExpr(cmd[1])
                    # If there are some mistakes in the expression, expressionVal will be None
                    if expressionVal != None:
                        # Valid expression
                        self.register[regNum] = expressionVal
                        self.commandList.append(nowCommand)
                    else:
                        print ('[ERROR] Invalid Input: ', nowCommand[1])
                        return 0
                else:
                    print ('[ERROR] Invalid Input: ', nowCommand[1])
                    return 0
            else:
                print ('[ERROR] Invalid Input: ', nowCommand[1])
                return 0
        return 1

    # Function for getting a command from buffer
    def getCommand(self):
        if self.buffQueue.empty:
            print('[ERROR] No buffed command')
        else:
            return self.buffQueue.get()
        
def main():
    inte = JJJInterpreter()
    while True:
        inputString = input()
        inte.addCommand(inputString)
        print(inte.getCommand())
        
if __name__ == "__main__":
    main()
