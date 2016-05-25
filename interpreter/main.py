'''
Command List:
up
down
left
right
jump
label
$1~$4
+ - * /
print=$1~$4 (command for debugging)
'''

global register
register = [-999, 0, 0, 0, 0]

# Function for parsing a single element (not a expression)
def getElementValue(exp):

    # Case for register element
    if exp[0] == '$':
        if len(exp) != 2:
            return None
        if exp[1] not in ['1', '2', '3', '4']:
            return None
        return register[ord(exp[1]) - ord('0')]

    # Case for constant element
    try:
        val = int(exp)
    except ValueError:
        return None
    return val

# Function for evaluating the value of a expression
def parseExpression(exp):

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
        return getElementValue(exp)

    # Case for non-constant expression
    expressionElement = exp.split(operatorType)
    val1 = getElementValue(expressionElement[0])
    val2 = getElementValue(expressionElement[1])
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

# Function for sending command to interpreter
def interpreterSend(cmd):

    # Remove spaces in command
    cmd = cmd.replace(" ", "")

    # Try to find "=" in command
    equalLocation = cmd.find("=")

    # equalLocation == -1  means the command is not a assignment
    if equalLocation == -1:

        # Command Types
        if cmd == "up":
            pass
        elif cmd == "down":
            pass
        elif cmd == "left":
            pass
        elif cmd == "right":
            pass
        elif cmd == "jump":
            pass
        elif cmd == "label":
            pass
        else:
            print '[ERROR] Invalid Input'

    else:

        # Assign/Operation Type
        cmd = cmd.split('=')

        # print=$1 command is for debugging
        if cmd[0] == 'print':
            if len(cmd[1]) == 2 and cmd[1][0] == '$' and cmd[1][1] in ['1', '2', '3', '4']:
                print 'value of ' + cmd[1] + ' = ' + str(register[ord(cmd[1][1])-ord('0')]);
        elif cmd[0][0] == '$':
            if cmd[0][1] in ['1', '2', '3', '4']:
                # Parse the assignment
                regNum = ord(cmd[0][1]) - ord('0')
                expressionVal = parseExpression(cmd[1])
                # If there are some mistakes in the expression, expressionVal will be None
                if expressionVal != None:
                    register[regNum] = expressionVal
                else:
                    print '[ERROR] Invalid Input'
            else:
                print '[ERROR] Invalid Input'
        else:
            print '[ERROR] Invalid Input'

def main():
    while True:
        str = raw_input()
        interpreterSend(str)

if __name__ == "__main__":
    main()
