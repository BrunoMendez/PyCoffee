from collections import deque
from constants import *


# Stack implementation to delimit deque library functionality (LIFO)
class Stack:
    def __init__(self):
        self.stack = deque()

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def push(self, item):
        self.stack.append(item)

    def size(self):
        return len(self.stack)

    def top(self):
        if len(self.stack) < 1:
            return None
        return self.stack[len(self.stack) - 1]

    def __str__(self):
        return str(list(self.stack))

    def empty(self):
        return len(self.stack) == 0

# Queue implementation to delimit deque library functionality (FIFO)
class Queue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if len(self.queue) < 1:
            return None
        return self.queue.popleft()

    def size(self):
        return len(self.queue)
    # Added this function to help us get the back of the queue
    def back(self):
        if len(self.queue) < 1:
            return None
        return self.queue.pop()

    def __str__(self):
        return str(list(self.queue))

    def empty(self):
        return len(self.queue) == 0

# Initialize semantic cube dictionary
semanticCube = {}
# Initialize valid types list
types = [ERROR, INT, FLOAT, CHAR, None]
# Initialize valid operators list
operator = [
    "+", "-", "*", "/", ">", "<", ">=", "<=", "==", "<>", "and", "or", "="
]
# Semantic cube logic since its a cube we iterate with a triple nested loop
# O(n^3)
for i in types:  # Left operand
    for j in types:  # Right operand
        for k in operator:  # Operators
            if (i == ERROR or j == ERROR or i == None or j == None
                    or k == None):
                semanticCube[(i, j, k)] = ERROR
            elif (i == INT and j == INT):
                semanticCube[(i, j, k)] = INT
            elif (i == FLOAT and j == FLOAT):
                if (k in ["+", "-", "*", "/", "="]):
                    semanticCube[(i, j, k)] = FLOAT
                elif (k in [AND, OR]):
                    semanticCube[(i, j, k)] = ERROR
                else:
                    semanticCube[(i, j, k)] = INT
            elif (i == CHAR and j == CHAR):
                if (k in ["<>", "=="]):
                    semanticCube[(i, j, k)] = INT
                elif (k == "="):
                    semanticCube[(i, j, k)] = CHAR
                else:
                    semanticCube[(i, j, k)] = ERROR
            elif ((i == INT and j == FLOAT) or (i == FLOAT and j == INT)):
                if (k in ["+", "-", "*", "/"]):
                    semanticCube[(i, j, k)] = FLOAT
                elif (k in [AND, OR, "="]):
                    semanticCube[(i, j, k)] = ERROR
                else:
                    semanticCube[(i, j, k)] = INT
            elif ((i == INT and j == CHAR) or (i == CHAR and j == INT)):
                semanticCube[(i, j, k)] = ERROR
            elif ((i == FLOAT and j == CHAR) or (i == CHAR and j == FLOAT)):
                semanticCube[(i, j, k)] = ERROR
            else:
                semanticCube[(i, j, k)] = ERROR

# Quadruple Class to manage same structure for quadruples:
# e.g of valid structure quadruple: operator, leftOperand, rightOperand and result
class Quadruple():
    def __init__(self, operator, leftOperand, rightOperand, result):
        self.operator = operator
        self.leftOperand = leftOperand
        self.rightOperand = rightOperand
        self.result = result

    def __str__(self):
        return (str(self.operator) + " " + str(self.leftOperand) + " " +
                str(self.rightOperand) + " " + str(self.result))

    def generateLista(self):
        return [
            self.operator, self.leftOperand, self.rightOperand, self.result
        ]
