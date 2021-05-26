from typing import Type
from errors import OutOfBounds, TypeMismatchError
import memory
from constants import *
from datastructures import Stack

instructionPointerStack = Stack()
resultAssignmentStack = Stack()
memoryStack = Stack()


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
        if isinstance(leftOperand, str) and "(" in leftOperand:
            leftOperand = memory.getValue(int(leftOperand[1:]))
        if isinstance(rightOperand, str) and "(" in rightOperand:
            rightOperand = memory.getValue(int(rightOperand[1:]))
        if isinstance(quad_result, str) and "(" in quad_result:
            quad_result = memory.getValue(int(quad_result[1:]))

        if operator == "+":
            result = memory.getValue(leftOperand) + memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "-":
            result = memory.getValue(leftOperand) - memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "/":
            result = memory.getValue(leftOperand) / memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == "*":
            result = memory.getValue(leftOperand) * memory.getValue(
                rightOperand)
            memory.setValue(quad_result, result)
        elif operator == '=':
            memory.setValue(quad_result, memory.getValue(leftOperand))
        elif operator == '<':
            result = memory.getValue(leftOperand) < memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '<=':
            result = memory.getValue(leftOperand) <= memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '>':
            result = memory.getValue(leftOperand) > memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '>=':
            result = memory.getValue(leftOperand) >= memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '==':
            result = memory.getValue(leftOperand) == memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == '<>':
            result = memory.getValue(leftOperand) != memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'and':
            result = memory.getValue(leftOperand) and memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'or':
            result = memory.getValue(leftOperand) or memory.getValue(
                rightOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == 'not':
            result = not memory.getValue(leftOperand)
            result = 1 if result else 0
            memory.setValue(quad_result, result)
        elif operator == PRINT_EXP:
            output[outputCount] = memory.getValue(quad_result)
            outputCount += 1
        elif operator == PRINT_STR:
            output[outputCount] = quad_result
            outputCount += 1
        elif operator == INPUT:
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
                    return output
                # pasar los stacks aqui
                memory.setValue(quad_result, inputValue)
                inputValue = None

            else:
                output[outputCount] = [INPUT_REQUEST, currentQuad]
                return output
        elif operator == GOTO:
            currentQuad = quad_result - 1
        elif operator == GOTOF:
            if memory.getValue(leftOperand) == 0:
                currentQuad = quad_result - 1
        elif operator == ERA:
            memoryStack.push(memory.LocalMemory())
        elif operator == END_FUNC:
            memory.local_memory_stack.pop()
            currentQuad = instructionPointerStack.pop()
        elif operator == PARAMETER:
            memoryStack.top().paramHelper(leftOperand)
        elif operator == GOSUB:
            memoryStack.top().assignParam()
            memory.local_memory_stack.push(memoryStack.pop())
            instructionPointerStack.push(currentQuad)
            if (memory.getType(leftOperand) != VOID):
                resultAssignmentStack.push(leftOperand)
            currentQuad = quad_result - 1
        elif operator == RETURN:
            functionAddress = resultAssignmentStack.pop()
            valueAddress = quad_result
            memory.setValue(functionAddress, memory.getValue(valueAddress))
            memory.local_memory_stack.pop()
            currentQuad = instructionPointerStack.pop()
        elif operator == END_PROG:
            output[outputCount] = "FIN!"
            return output
        elif operator == VERIFY_ARR:
            s = memory.getValue(leftOperand)
            lim = rightOperand
            if not (0 <= s < lim):
                raise OutOfBounds
        currentQuad += 1
    return output
