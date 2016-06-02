from enum import Enum
import queue
from pyparsing import Word, nums, alphas, Combine, oneOf, opAssoc, operatorPrecedence

class JJJInterpreter:
     
    def __init__(self, buff_size = 3):
        
        # CONFIG
        self.BUFF_SIZE = buff_size # How much prediction will be made by the interpreter
        self.REGISTER_NO = 4       # How many registers are available for a player
        
        # DON'T MODIFY
        self.isLabeled = 0
        self.commandList = []
        self.register = {}
        self.registerMap = {}
        for i in range(1, self.REGISTER_NO + 1):
            key = '$' + str(i)
            value = chr( ord('A') + i - 1 )
            self.register[value] = 0
            self.registerMap[key] = value
        self.buffQueue = queue.Queue()
        # define the parser
        self.integer = Word(nums)
        self.variable = Word(alphas,exact=1)
        self.operand = self.integer | self.variable
        
        self.signop = oneOf('+ -')
        self.multop = oneOf('* /')
        self.plusop = oneOf('+ -')
        
        # use parse actions to attach EvalXXX constructors to sub-expressions
        self.operand.setParseAction(self.EvalConstant)
        self.arith_expr = operatorPrecedence(self.operand,
            [
             (self.signop, 1, opAssoc.RIGHT, self.EvalSignOp),
             (self.multop, 2, opAssoc.LEFT, self.EvalMultOp),
             (self.plusop, 2, opAssoc.LEFT, self.EvalAddOp),
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
        
    def operatorOperands(self, tokenlist):
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
            if self.value in self.EvalConstant.variables:
                return self.EvalConstant.variables[self.value]
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
            for op,val in self.operatorOperands(self.value[1:]):
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
            for op,val in self.operatorOperands(self.value[1:]):
                if op == '+':
                    sum += val.eval()
                if op == '-':
                    sum -= val.eval()
            return sum
        
    def commandTranslate(self, cmd):
        # Remove spaces in command
        cmd = cmd.replace(" ", "")
        # Replace the register name with its variable name in interpreter
        for key, value in self.registerMap.items():
            cmd = cmd.replace(key, value)
        return cmd
        
    def procAssignCmd(self, cmd):
        cmd = cmd.split('=')
        # Parse left expression
        if len(cmd[0]) > 1 or len(cmd[0]) == 0:
            return 0
        if ord(cmd[0]) not in range(ord('A'), ord('A') + self.REGISTER_NO - 1):
            return 0
        try:
            self.register[cmd[0]] = eval(cmd[1], self.register)
            print (cmd[0] + '=' + str(self.register[cmd[0]]))
            return 1
        except:
            return 0
        
    # Function for adding command to interpreter, return 1 on success, 0 on fail
    def addCommand(self, cmd):
        newCommand = cmd
        # Translate command first
        cmd = self.commandTranslate(cmd)
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
                # Set a label for jump
                if ( len(self.commandList) > 0 ):
                    del self.commandList[:]
                # Set labeled flag
                self.isLabeled = 1
            else:
                print ('[ERROR] Invalid Input: ', newCommand)
                return 0
        else:
            # Assign/Operation Type
            nowCommand = (self.CommandType.assign, cmd)
            ret = self.procAssignCmd(cmd)
            if ret == 1:
                self.commandList.append(nowCommand)
            else:
                print ('[ERROR] Invalid Input: ', newCommand)
                return 0
        return 1

    # Function for getting a command from buffer
    def getCommand(self):
        if self.buffQueue.empty:
            #print('[ERROR] No buffed command')
            pass
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
