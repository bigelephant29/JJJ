from enum import Enum
import queue
from pyparsing import Word, nums, alphas, Combine, oneOf, opAssoc, operatorPrecedence

def operatorOperands(tokenlist):
    it = iter(tokenlist)
    while 1:
        try:
            yield (next(it), next(it))
        except StopIteration:
            break

class EvalConstant(object):
    variables = {}
    def __init__(self, tokens):
        self.value = tokens[0]
    def eval(self):
        if self.value in EvalConstant.variables:
            return EvalConstant.variables[self.value]
        else:
            return int(float(self.value))

class EvalSignOp(object):
    def __init__(self, tokens):
        self.sign, self.value = tokens[0]
    def eval(self):
        mult = {'+':1, '-':-1}[self.sign]
        return mult * self.value.eval()

class EvalMultOp(object):
    def __init__(self, tokens):
        self.value = tokens[0]
    def eval(self):
        prod = self.value[0].eval()
        for op,val in operatorOperands(self.value[1:]):
            if op == '*':
                prod *= val.eval()
            if op == '/':
                prod /= val.eval()
        return int(prod)
    
class EvalAddOp(object):
    def __init__(self, tokens):
        self.value = tokens[0]
    def eval(self):
        sum = self.value[0].eval()
        for op,val in operatorOperands(self.value[1:]):
            if op == '+':
                sum += val.eval()
            if op == '-':
                sum -= val.eval()
        return sum

class JJJInterpreter:
     
    def __init__(self, buff_size = 3):
        
        # CONFIG
        #self.BUFF_SIZE = buff_size # How much prediction will be made by the interpreter
        self.REGISTER_NO = 4       # How many registers are available for a player
        
        # DON'T MODIFY
        self.isLabeled = 0
        self.isJumped = 0
        self.commandList = []
        self.register = {}
        self.registerMap = {}
        for i in range(1, self.REGISTER_NO + 1):
            key = '$' + str(i)
            value = chr( ord('A') + i - 1 )
            self.register[value] = 0
            self.registerMap[key] = value
        self.buffQueue = queue.Queue()
        self.nowExecute = 0

        # Parser Configuration
        self.integer = Word(nums)
        self.variable = Word(alphas,exact=1)
        self.operand = self.integer | self.variable
        
        self.signop = oneOf('+ -')
        self.multop = oneOf('* /')
        self.plusop = oneOf('+ -')
        
        self.operand.setParseAction(EvalConstant)
        self.arith_expr = operatorPrecedence(self.operand,
            [
             (self.signop, 1, opAssoc.RIGHT, EvalSignOp),
             (self.multop, 2, opAssoc.LEFT, EvalMultOp),
             (self.plusop, 2, opAssoc.LEFT, EvalAddOp),
            ])
        
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
        
    # Function for transforming original command form into executable command form
    def commandTranslate(self, cmd):
        # Remove spaces in command
        cmd = cmd.replace(' ', '')
        # Replace the register name with its variable name in interpreter
        for key, value in self.registerMap.items():
            cmd = cmd.replace(key, value)
        return cmd
    
    # Function for processing assign statement, assign value to register when assign = 1
    def procAssignCmd(self, cmd, assign = 0):
        cmd = cmd.split('=')
        # Parse left expression
        if len(cmd[0]) > 1 or len(cmd[0]) == 0:
            return 0
        if ord(cmd[0]) not in range(ord('A'), ord('A') + self.REGISTER_NO - 1):
            return 0
        try:
            if assign == 1:
                EvalConstant.variables = self.register
                self.register[cmd[0]] = self.arith_expr.parseString(cmd[1])[0].eval()
            else:
                EvalConstant.variables = self.register
                self.arith_expr.parseString(cmd[1])[0].eval()
            return 1
        except:
            return 0
        
    # Function for looping between label-jump pair
    def runCommand(self, stop = 1):
        jumped = 0
        if self.isLabeled == 0:
            return
        if len(self.commandList) == 0:
            return
        while 1:
            if self.nowExecute == len(self.commandList):
                return
            elif self.commandList[self.nowExecute][0] == self.CommandType.up:
                self.buffQueue.put(self.CommandType.up)
                self.nowExecute += 1
                if stop == 1:
                    return
            elif self.commandList[self.nowExecute][0] == self.CommandType.down:
                self.buffQueue.put(self.CommandType.down)
                self.nowExecute += 1
                if stop == 1:
                    return
            elif self.commandList[self.nowExecute][0] == self.CommandType.left:
                self.buffQueue.put(self.CommandType.left)
                self.nowExecute += 1
                if stop == 1:
                    return
            elif self.commandList[self.nowExecute][0] == self.CommandType.right:
                self.buffQueue.put(self.CommandType.right)
                self.nowExecute += 1
                if stop == 1:
                    return 
            elif self.commandList[self.nowExecute][0] == self.CommandType.jump:
                if jumped == 1:
                    return
                self.nowExecute = 0
                if stop == 0:
                    return
                jumped = 1
            elif self.commandList[self.nowExecute][0] == self.CommandType.assign:
                self.procAssignCmd(self.commandList[self.nowExecute][1], 1)
                self.nowExecute += 1
        
    # Function for adding command to interpreter, return 1 on success, 0 on fail
    def addCommand(self, cmd):
        newCommand = cmd
        if self.isJumped and cmd != 'label':
            print ('[ERROR] You have to set a new label first')
            return 0
        # Try to find '=' in command
        equalLocation = cmd.find('=')
        # equalLocation == -1  means the command is not a assignment
        if equalLocation == -1:
            # Command Types
            if cmd == 'up':
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.up,));
                else:
                    self.buffQueue.put(self.CommandType.up)
            elif cmd == 'down':
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.down,));
                else:
                    self.buffQueue.put(self.CommandType.down)
            elif cmd == 'left':
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.left,));
                else:
                    self.buffQueue.put(self.CommandType.left)
            elif cmd == 'right':
                if self.isLabeled == 1:
                    self.commandList.append((self.CommandType.right,));
                else:
                    self.buffQueue.put(self.CommandType.right)
            elif cmd == 'jump':
                if self.isLabeled == 1:
                    self.isJumped = 1
                    self.commandList.append((self.CommandType.jump,));
                else:
                    print ('[ERROR] No label for jumping')
                    return 0
            elif cmd == 'label':
                # Set a label for jump
                if ( len(self.commandList) > 0 ):
                    self.runCommand(0)
                    del self.commandList[:]
                # Set labeled flag
                self.isLabeled = 1
                self.isJumped = 0
            else:
                print ('[ERROR] Invalid Input: ', newCommand)
                return 0
        else:
            # Assign/Operation Type
            nowCommand = (self.CommandType.assign, cmd)
            ret = self.procAssignCmd(cmd)
            if ret == 1:
                if self.isLabeled == 1:
                    self.commandList.append(nowCommand)
                else:
                    self.procAssignCmd(cmd, 1)
            else:
                print ('[ERROR] Invalid Input: ', newCommand)
                return 0
        return 1
        
    # Function for checking the validation of multiline input    
    def sendCommand(self, cmd):
        tmpisJumped = self.isJumped
        tmpisLabeled = self.isLabeled
        newCommand = cmd.split('\n')
        for i in range(0, len(newCommand)):
            # Translate command first
            saveCommand = newCommand[i]
            newCommand[i] = self.commandTranslate(newCommand[i])
            if len(newCommand[i]) == 0:
                continue
            if tmpisJumped and newCommand[i] != 'label':
                print ('[ERROR] You have to set a new label first')
                return i
            # Try to find '=' in command
            equalLocation = newCommand[i].find('=')
            # equalLocation == -1  means the command is not a assignment
            if equalLocation == -1:
                # Command Types
                if newCommand[i] == 'up':
                    pass
                elif newCommand[i] == 'down':
                    pass
                elif newCommand[i] == 'left':
                    pass
                elif newCommand[i] == 'right':
                    pass
                elif newCommand[i] == 'jump':
                    if  tmpisLabeled == 1:
                        tmpisJumped = 1
                    else:
                        print ('[ERROR] No label for jumping')
                        return i
                elif newCommand[i] == 'label':
                    tmpisLabeled = 1
                    tmpisJumped = 0
                else:
                    print ('[ERROR] Invalid Input: ', saveCommand)
                    return i
            else:
                # Assign/Operation Type
                ret = self.procAssignCmd(newCommand[i])
                if ret == 1:
                    pass
                else:
                    print ('[ERROR] Invalid Input: ', saveCommand)
                    return i
        for line in newCommand:
            self.addCommand(line)
        return -1
        
    # Function for getting a command from buffer
    def getCommand(self):
        if self.buffQueue.empty():
            self.runCommand()
            if self.buffQueue.empty():
                print ('[ERROR] No command for executing')
                return None
            else:
                return self.buffQueue.get()
        else:
            return self.buffQueue.get()
           
    # Function for debugging, just ignore it :)
    def printReg(self):
        for key, value in self.register.items():
            print (key + ' : ' + str(value))
        
def main():
    inte = JJJInterpreter()
    inte.sendCommand('up\ndown\nleft\nright\nfuck')
    while True:
        inputString = input()
        if inputString == 'print':
            inte.printReg()
        elif inputString == 'get':
            print(inte.getCommand())
        else:
            inte.sendCommand(inputString)
        
if __name__ == '__main__':
    main()
