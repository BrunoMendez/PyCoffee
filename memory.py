from constants import *
from datastructures import Queue, Stack

types = {
    GLOBAL_INT: 1000,
    GLOBAL_FLOAT: 2000,
    GLOBAL_CHAR: 3000,
    LOCAL_INT: 4000,
    LOCAL_FLOAT: 5000,
    LOCAL_CHAR: 6000,
    TEMPORAL_INT: 7000,
    TEMPORAL_FLOAT: 8000,
    TEMPORAL_CHAR: 9000,
    CONSTANT_INT: 10000,
    CONSTANT_FLOAT: 11000,
    CONSTANT_CHAR: 12000,
    VOID: 13000,
    TEMPORAL_LOCAL_INT: 14000,
    TEMPORAL_LOCAL_FLOAT: 15000,
    TEMPORAL_LOCAL_CHAR: 16000
}


class LocalMemory():
    def __init__(self):
        self.memory = {}
        self.paramInts = Queue()
        self.paramFloats = Queue()
        self.paramChars = Queue()
    
    def getValue(self, address):
        return self.memory[address]

    def setValue(self, address, value):
        self.memory[address] = value

    def printMem(self):
        print(self.memory)
    def paramHelper(self, valueAddress):
        value = getValue(valueAddress)
        valueType = getType(valueAddress)
        if valueType == INT:
            self.paramInts.enqueue(value)
        elif valueType == FLOAT:
            self.paramFloats.enqueue(value)
        elif valueType == CHAR:
            self.paramChars.enqueue(value)

    def assignParam(self):
        sizeInts = self.paramInts.size()
        for index in range(0, sizeInts):
            self.memory[index + 4000] = self.paramInts.dequeue()
        sizeFloats = self.paramFloats.size()
        for index in range(0, sizeFloats):
            self.memory[index + 5000] = self.paramFloats.dequeue()
        sizeChars = self.paramChars.size()
        for index in range(0, sizeChars):
            self.memory[index + 6000] = self.paramChars.dequeue()
class GlobalMemory():
    def __init__(self):
        self.memory = {}

    def getValue(self, address):
        return self.memory[address]

    def setValue(self, address, value):
        self.memory[address] = value

    def printMem(self):
        print(self.memory)


global_memory = GlobalMemory()
local_memory_stack = Stack()


def getType(address):
    if (1000 <= address <= 1999 or 4000 <= address <= 4999
            or 7000 <= address <= 7999 or 10000 <= address <= 10999
            or 14000 <= address <= 14999):
        return INT
    elif (2000 <= address <= 2999 or 5000 <= address <= 5999
          or 8000 <= address <= 8999 or 11000 <= address <= 11999
          or 15000 <= address <= 15999):
        return FLOAT
    elif (3000 <= address <= 3999 or 6000 <= address <= 6999
          or 9000 <= address <= 9999 or 12000 <= address <= 12999
          or 16000 <= address <= 16999):
        return CHAR
    elif 13000 <= address <= 13999:
        return VOID



def getNextAddress(mem, offset=1, value=None, valType=None):
    current_address = types[mem]
    # parse value
    if valType == INT:
        value = int(value)
    elif valType == FLOAT:
        value = float(value)

    # if value store value

    if valType != None and value != None:
        global_memory.setValue(current_address, value)
    types[mem] = types[mem] + offset
    if types[mem] % 1000 != 0:
        return current_address
    else:
        raise MemoryError


def isLocal(address):
    return (address >= 4000 and address < 7000) or (address >= 14000
                                                    and address < 17000)


def getValue(address):
    if isLocal(address):
        return local_memory_stack.top().getValue(address)
    else:
        return global_memory.getValue(address)


def setValue(address, value):
    if isLocal(address):
        return local_memory_stack.top().setValue(address, value)
    else:
        return global_memory.setValue(address, value)


def resetLocalTemporals():
    countInt = types[TEMPORAL_LOCAL_INT] - 14000
    countFloat = types[TEMPORAL_LOCAL_FLOAT] - 15000
    countChar = types[TEMPORAL_LOCAL_CHAR] - 16000
    types[TEMPORAL_LOCAL_INT] = 14000
    types[TEMPORAL_LOCAL_FLOAT] = 15000
    types[TEMPORAL_LOCAL_CHAR] = 16000
    return [countInt, countFloat, countChar]


def resetLocals():
    countInt = types[LOCAL_INT] - 4000
    countFloat = types[LOCAL_FLOAT] - 5000
    countChar = types[LOCAL_CHAR] - 6000
    types[LOCAL_INT] = 4000
    types[LOCAL_FLOAT] = 5000
    types[LOCAL_CHAR] = 6000
    return [countInt, countFloat, countChar]


def getVarCounts():
    countInt = types[GLOBAL_INT] - 1000
    countFloat = types[GLOBAL_FLOAT] - 2000
    countChar = types[GLOBAL_CHAR] - 3000
    countTempInt = types[TEMPORAL_INT] - 7000
    countTempFloat = types[TEMPORAL_CHAR] - 8000
    countTempChar = types[TEMPORAL_CHAR] - 9000
    return [
        countInt, countFloat, countChar, countTempInt, countTempFloat,
        countTempChar
    ]


def resetAll():
    global types
    global global_memory
    types = {
        GLOBAL_INT: 1000,
        GLOBAL_FLOAT: 2000,
        GLOBAL_CHAR: 3000,
        LOCAL_INT: 4000,
        LOCAL_FLOAT: 5000,
        LOCAL_CHAR: 6000,
        TEMPORAL_INT: 7000,
        TEMPORAL_FLOAT: 8000,
        TEMPORAL_CHAR: 9000,
        CONSTANT_INT: 10000,
        CONSTANT_FLOAT: 11000,
        CONSTANT_CHAR: 12000,
        VOID: 13000,
        TEMPORAL_LOCAL_INT: 14000,
        TEMPORAL_LOCAL_FLOAT: 15000,
        TEMPORAL_LOCAL_CHAR: 16000
    }
    global_memory = GlobalMemory()
    while (not local_memory_stack.empty()):
        local_memory_stack.pop()


""" def getValue(address):
    return global_memory[address]


def setValue(address, value):
    global_memory[address] = value


def printMem():
    print("Memory:", global_memory)
 """