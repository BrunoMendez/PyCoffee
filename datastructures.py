from collections import deque


# Una pila LIFO con los metodos basicos
# Usamos esta clase para limitar el uso de funciones de la
# libreria deque a solo las necesarias para una pila
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

    def __str__(self):
        return str(list(self.queue))

    def empty(self):
        return len(self.queue) == 0


semanticCube = {}

types = ["error", "int", "float", "char"]

operator = [
    "+", "-", "*", "/", ">", "<", ">=", "<=", "==", "<>", "and", "or", "="
]

for i in types:  # Left operand
    for j in types:  # Right operand
        for k in operator:  # Operators
            if (i == "error" or j == "error"):
                semanticCube[(i, j, k)] = "error"
            elif (i == "int" and j == "int"):
                semanticCube[(i, j, k)] = "int"
            elif (i == "float" and j == "float"):
                if (k in ["+", "-", "*", "/", "="]):
                    semanticCube[(i, j, k)] = "float"
                elif (k in ["and", "or"]):
                    semanticCube[(i, j, k)] = "error"
                else:
                    semanticCube[(i, j, k)] = "int"
            elif (i == "char" and j == "char"):
                if (k in ["<>", "=="]):
                    semanticCube[(i, j, k)] = "int"
                elif (k == "="):
                    semanticCube[(i, j, k)] = "char"
                else:
                    semanticCube[(i, j, k)] = "error"
            elif ((i == "int" and j == "float")
                  or (i == "float" and j == "int")):
                if (k in ["+", "-", "*", "/"]):
                    semanticCube[(i, j, k)] = "float"
                elif (k in ["and", "or", "="]):
                    semanticCube[(i, j, k)] = "error"
                else:
                    semanticCube[(i, j, k)] = "int"
            elif ((i == "int" and j == "char")
                  or (i == "char" and j == "int")):
                semanticCube[(i, j, k)] = "error"
            elif ((i == "float" and j == "char")
                  or (i == "char" and j == "float")):
                semanticCube[(i, j, k)] = "error"
            else:
                semanticCube[(i, j, k)] = "error"


class Quadruple():
    def __init__(self, operator, leftOperand, rightOperand, result):
        self.operator = operator
        self.leftOperand = leftOperand
        self.rightOperand = rightOperand
        self.result = result

    def __str__(self):
        return (str(self.operator) + " " + str(self.leftOperand) + " " +
                str(self.rightOperand) + " " + str(self.result))