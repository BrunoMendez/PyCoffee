from errors import OutOfBounds, TypeMismatchError
import memory
from constants import *
from datastructures import Stack

# Initialize global variables
# Stack to check where the instuction pointer left
# Breadcrumbs for recursive calls
instructionPointerStack = Stack()
# Stack to manage recursive assignment
resultAssignmentStack = Stack()
# Stack to manage setting parameters to function's local memory before setting the function's local memory as the current local memory
# This helps us call functions as parameters
# memoryStack has instances of memory
memoryStack = Stack()

# Function to start the vm and do juicy stuff!
# Receives list of quadruples and optionally the currentQuad and inputValue
# Will receive the currentQuad and inputValue after vm stops for input response
# Returns list of outputs (PRINTS)
def start(quadruples, currentQuad=0, inputValue=None):
    global instructionPointerStack
    global resultAssignmentStack
    global memoryStack
    outputCount = 0
    output = {}
    while currentQuad < len(quadruples):
        quad = quadruples[currentQuad]
        print(quad)
        operator = quad.operator
        leftOperand = quad.leftOperand
        rightOperand = quad.rightOperand
        quad_result = quad.result
        # Checks if pointer and gets address
        if isinstance(leftOperand, str) and "(" in leftOperand:
            leftOperand = memory.getValue(int(leftOperand[1:]))
        # Checks if pointer and gets address
        if isinstance(rightOperand, str) and "(" in rightOperand:
            rightOperand = memory.getValue(int(rightOperand[1:]))
        # Checks if pointer and gets address
        if isinstance(quad_result, str) and "(" in quad_result:
            quad_result = memory.getValue(int(quad_result[1:]))
        if operator == "+":
            # Get value from addresses and perform sum
            result = memory.getValue(leftOperand) + memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "-":
            # Get value from addresses and perform substraction
            result = memory.getValue(leftOperand) - memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "/":
            # Get value from addresses and perform division
            result = memory.getValue(leftOperand) / memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "*":
            # Get value from addresses and perform multiplication
            result = memory.getValue(leftOperand) * memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == '=':
            # Get value from addresses and perform assignment
            memory.setValue(quad_result, memory.getValue(leftOperand))
        elif operator == '<':
            # Get value from addresses and perform less than operation
            result = memory.getValue(leftOperand) < memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '<=':
            # Get value from addresses and perform less than or equal operation
            result = memory.getValue(leftOperand) <= memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '>':
            # Get value from addresses and perform greater than operation
            result = memory.getValue(leftOperand) > memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '>=':
            # Get value from addresses and perform greater than or equal operation
            result = memory.getValue(leftOperand) >= memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '==':
            # Get value from addresses and perform greater comparison(equal) operation
            result = memory.getValue(leftOperand) == memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '<>':
            # Get value from addresses and perform not equal operation
            result = memory.getValue(leftOperand) != memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'and':
            # Get value from addresses and perform AND operation
            result = memory.getValue(leftOperand) and memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'or':
            # Get value from addresses and perform OR operation
            result = memory.getValue(leftOperand) or memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'not':
            # Get value from addresses and perform NOT operation
            result = not memory.getValue(leftOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == PRINT_EXP:
            # Get value from addresses and perform print expression operation
            output[outputCount] = memory.getValue(quad_result)
            outputCount += 1
        elif operator == PRINT_STR:
            # Get value from addresses and perform print sign operation
            output[outputCount] = quad_result
            outputCount += 1
        elif operator == INPUT:
            # Get input value, cast and set memory value
            if inputValue != None:
                varType = leftOperand
                try:
                    if varType == INT:
                        inputValue = int(inputValue)
                    elif varType == FLOAT:
                        inputValue = float(inputValue)
                    elif varType == CHAR:
                        if len(inputValue) != 1:
                            raise TypeMismatchError
                except ValueError:
                    output[outputCount] = "Type mismatch error"
                    # Return error to the front
                    return output
                memory.setValue(quad_result, inputValue)
                inputValue = None
            else:
                # If input value was set return output
                output[outputCount] = [INPUT_REQUEST, currentQuad]
                return output
        elif operator == GOTO:
            # Perform GOTO operations
            currentQuad = quad_result - 1
        elif operator == GOTOF:
            # Perform GOTOF operations
            if memory.getValue(leftOperand) == 0:
                currentQuad = quad_result - 1
        elif operator == ERA:
            # Push an instance of localMemory to expect a function
            memoryStack.push(memory.LocalMemory())
        elif operator == END_FUNC:
            # Perform ENDFUNC operation and pop instance of the local memory stack
            memory.local_memory_stack.pop()
            currentQuad = instructionPointerStack.pop()
        elif operator == PARAMETER:
            # Perform PARAMETER operations
            memoryStack.top().paramHelper(leftOperand)
        elif operator == GOSUB:
            # Perform GOSUB operations
            # Get the top of the memoryStack and assign an address
            memoryStack.top().assignParam()
            # Push instance of localMemory
            memory.local_memory_stack.push(memoryStack.pop())
            instructionPointerStack.push(currentQuad)
            if (memory.getType(leftOperand) != VOID):
                resultAssignmentStack.push(leftOperand)
            currentQuad = quad_result - 1
        elif operator == RETURN:
            # Perform RETURN operations
            functionAddress = resultAssignmentStack.pop()
            valueAddress = quad_result
            memory.setValue(functionAddress, memory.getValue(valueAddress))
            # Pop instance of the local memory
            memory.local_memory_stack.pop()
            # Pop instructionPointer
            currentQuad = instructionPointerStack.pop()
        elif operator == END_PROG:
            # Perform ENDPROG operations
            output[outputCount] = "FIN!"
            return output
        elif operator == VERIFY_ARR:
            # Perform VERIFYARR operations
            s = memory.getValue(leftOperand)
            lim = rightOperand
            # Checks that the array is not out of bounds!
            if not (0 <= s < lim):
                raise OutOfBounds
        currentQuad += 1
    return output
