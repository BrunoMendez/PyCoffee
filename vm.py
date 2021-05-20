from typing import Type
from errors import TypeMismatchError
import memory
from constants import *


def start(quadruples, currentQuad=0, inputValue=None):
    outputCount = 0
    output = {}
    memory.printMem()
    while currentQuad < len(quadruples):
        quad = quadruples[currentQuad]
        operator = quad.operator
        leftOperand = quad.leftOperand
        rightOperand = quad.rightOperand
        quad_result = quad.result
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
                memory.setValue(quad_result, inputValue)
                inputValue = None
            else:
                output[outputCount] = [INPUT_REQUEST, currentQuad]
                return output
        elif operator == GOTO:
            if leftOperand == MAIN:
                currentQuad = quad_result - 1
        elif operator == END_PROG:
            output[outputCount] = "FIN!"
            return output
        currentQuad += 1
    return output
