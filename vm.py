from memory import *
from constants import *

currentQuad = 0


def start(quadruples):
    global currentQuad
    while currentQuad < len(quadruples):
        print(currentQuad)
        quad = quadruples[currentQuad]
        operator = quad.operator
        leftOperand = quad.leftOperand
        rightOperand = quad.rightOperand
        quad_result = quad.result
        if operator == "+":
            result = memory[leftOperand] + memory[rightOperand]
            memory[quad_result] = result
        elif operator == "-":
            result = memory[leftOperand] - memory[rightOperand]
            memory[quad_result] = result
        elif operator == "/":
            result = memory[leftOperand] / memory[rightOperand]
            memory[quad_result] = result
        elif operator == "*":
            result = memory[leftOperand] * memory[rightOperand]
            memory[quad_result] = result
        elif operator == GOTO:
            if leftOperand == MAIN:
                currentQuad = quad_result - 1
        elif operator == END_PROG:
            break
        currentQuad += 1
        print("$$$")
        print(memory)
        print("@@@")
        print(quad)
        print("###")
