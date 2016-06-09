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
        self.commandList = []
        self.register = {}
        self.registerMap = {}
        self.labelDict = {}
        for i in range(1, self.REGISTER_NO + 1):
            key = '$' + str(i)
            value = chr( ord('A') + i - 1 )
            self.register[value] = 0
            self.registerMap[key] = value
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
        
    def initialize(self):
        del self.commandList[:]
        self.commandList = []
        self.register.clear()
        self.registerMap.clear()
        for i in range(1, self.REGISTER_NO + 1):
            key = '$' + str(i)
            value = chr( ord('A') + i - 1 )
            self.register[value] = 0
            self.registerMap[key] = value
        self.nowExecute = 0
        
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
    def getCommand(self):
        while 1:
            if self.nowExecute == len(self.commandList):
                return None
            elif self.commandList[self.nowExecute][0] == self.CommandType.up:
                self.nowExecute += 1
                return self.CommandType.up
            elif self.commandList[self.nowExecute][0] == self.CommandType.down:
                self.nowExecute += 1
                return self.CommandType.down
            elif self.commandList[self.nowExecute][0] == self.CommandType.left:
                self.nowExecute += 1
                return self.CommandType.left
            elif self.commandList[self.nowExecute][0] == self.CommandType.right:
                self.nowExecute += 1
                return self.CommandType.right
            elif self.commandList[self.nowExecute][0] == self.CommandType.jump:
                self.nowExecute = self.labelDict[self.commandList[self.nowExecute][1]]
            elif self.commandList[self.nowExecute][0] == self.CommandType.assign:
                self.procAssignCmd(self.commandList[self.nowExecute][1], 1)
                self.nowExecute += 1
            else:
                self.nowExecute += 1
        
    # Function for checking the validation of multiline input    
    def sendCommand(self, cmd):
        newCommand = cmd.split('\n')
        newCommandList = []
        newLabelDict = {}
        for i in range(0, len(newCommand)):
            # Translate command first
            saveCommand = newCommand[i] #save command for 
            newCommand[i] = self.commandTranslate(newCommand[i])
            if len(newCommand[i]) == 0:
                continue
            # Try to find '=' in command
            equalLocation = newCommand[i].find('=')
            # equalLocation == -1  means the command is not a assignment
            if equalLocation == -1:
                # Command Types
                if newCommand[i] == 'up':
                    newCommandList.append((self.CommandType.up,));
                elif newCommand[i] == 'down':
                    newCommandList.append((self.CommandType.down,));
                elif newCommand[i] == 'left':
                    newCommandList.append((self.CommandType.left,));
                elif newCommand[i] == 'right':
                    newCommandList.append((self.CommandType.right,));
                elif newCommand[i].startswith('jump'):
                    sub = newCommand[i][4:]
                    try:
                        sub = int(sub)
                    except:
                        print ('[ERROR] not an integer label')
                        return i
                    if sub not in newLabelDict:
                        print ('[ERROR] not an existing label')
                        return i
                    newCommandList.append((self.CommandType.jump,sub));
                elif newCommand[i].startswith('label'):
                    sub = newCommand[i][5:]
                    try:
                        sub = int(sub)
                    except:
                        print ('[ERROR] not an integer label')
                        return i
                    newLabelDict[sub] = i
                    newCommandList.append((self.CommandType.label,sub));
                else:
                    print ('[ERROR] Invalid Input: ', saveCommand)
                    return i
            else:
                # Assign/Operation Type
                ret = self.procAssignCmd(newCommand[i])
                if ret == 1:
                    newCommandList.append((self.CommandType.assign,newCommand[i]))
                else:
                    print ('[ERROR] Invalid Input: ', saveCommand)
                    return i
        self.initialize()
        del self.commandList[:]
        self.commandList = newCommandList
        self.labelDict = newLabelDict
        return -1
        
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
