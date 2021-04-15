
from collections import deque

# Una pila LIFO con los metodos basicos
# Usamos esta clase para limitar el uso de funciones de la 
# libreria deque a solo las necesarias para una pila
class Stack:

    def __init__(self):
        print("working")
        self.stack = deque()

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def push(self, item):
        self.stack.append(item)

    def size(self):
        return len(self.stack)

    def __str__(self):
        return str(list(self.stack))

    def empty(self):
        if len(self.stack) == 0: return True; return False

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
        if len(self.queue) == 0: return True; return False

