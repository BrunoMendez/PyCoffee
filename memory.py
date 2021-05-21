from constants import *
from datastructures import Stack


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
class LocalMemory() :
    def __init__(self):
        self.arrInts = []
        self.arrFloats = []
        self.arrChars = []
        self.tempInts = []
        self.tempFloats = []
        self.tempChars = []
    def getValue(self,address):
        if address >= 4000 and address <= 4999:
            address = address - 4000
            return self.arrInts[address]
        elif address >= 5000 and address <= 5999:
            address = address - 5000
            return self.arrFloats[address]
        elif address >= 6000 and address <= 6999:
            address = address - 6000
            return self.arrChars[address]
        elif address >= 14000 and address <= 14999:
            address = address - 14000
            return self.tempInts[address]
        elif address >= 15000 and address <= 15999:
            address = address - 15000
            return self.tempFloats[address]
        elif address >= 16000 and address <= 16999:
            address = address - 16000
            return self.tempChars[address]
        else: 
            raise MemoryError

    def setValue(self,address, value):
        if address >= 4000 and address <= 4999:
            address = address - 4000
            if address == len(self.arrInts):
                self.arrInts.append(value)
            else:
                self.arrInts[address] = value
            return
        elif address >= 5000 and address <= 5999:
            address = address - 5000
            if address == len(self.arrFloats):
                self.arrFloats.append(value)
            else:
                self.arrFloats[address] = value
            return
        elif address >= 6000 and address <= 6999:
            address = address - 6000
            if address == len(self.arrChars):
                self.arrChars.append(value)
            else:
                self.arrChars[address] = value
            return
        elif address >= 14000 and address <= 14999:
            address = address - 14000
            if address == len(self.tempInts):
                self.tempInts.append(value)
            else:
                self.tempInts[address] = value
            return
        elif address >= 15000 and address <= 15999:
            address = address - 15000
            if address == len(self.tempFloats):
                self.tempFloats.append(value)
            else:
                self.tempFloats[address] = value
            return
        elif address >= 16000 and address <= 16999:
            address = address - 16000
            if address == len(self.tempChars):
                self.tempChars.append(value)
            else:
                self.tempChars[address] = value
            return
        else:
            raise MemoryError

    def printMem(self):
        print(self.arrInts)
        print(self.arrFloats)
        print(self.arrChars)
        print(self.tempInts)
        print(self.tempFloats)
        print(self.tempChars)

class GlobalMemory():
    def __init__(self):
        self.arrInts = []
        self.arrFloats = []
        self.arrChars = []
        self.tempInts = []
        self.tempFloats = []
        self.tempChars = []
        self.constInts = []
        self.constFloats = []
        self.constChars = []
        self.voidfunctions = []
    def getValue(self,address):
        if address >= 1000 and address <= 1999:
            address = address - 1000
            return self.arrInts[address]
        elif address >= 2000 and address <= 2999:
            address = address - 2000
            return self.arrFloats[address]
        elif address >= 3000 and address <= 3999:
            address = address - 6000
            return self.arrChars[address]
        elif address >= 7000 and address <= 7999:
            address = address - 7000
            return self.tempInts[address]
        elif address >= 8000 and address <= 8999:
            address = address - 8000
            return self.tempFloats[address]
        elif address >= 9000 and address <= 9999:
            address = address - 9000
            return self.tempChars[address]
        elif address >= 10000 and address <= 10999:
            address = address - 10000
            return self.constInts[address]
        elif address >= 11000 and address <= 11999:
            address = address - 11000
            return self.constFloats[address]
        elif address >= 12000 and address <= 12999:
            address = address - 12000
            return self.constChars[address]
        elif address >= 13000 and address <= 13999:
            address = address - 13000
            return self.voidfunctions[address]
        else: 
            raise MemoryError

    def setValue(self,address, value):
        if address >= 1000 and address <= 1999:
            address = address - 1000
            if address == len(self.arrInts):
                self.arrInts.append(value)
            else:
                self.arrInts[address] = value
            return
        elif address >= 2000 and address <= 2999:
            address = address - 2000
            if address == len(self.arrFloats):
                self.arrFloats.append(value)
            else:
                self.arrFloats[address] = value
            return
        elif address >= 3000 and address <= 3999:
            address = address - 3000
            if address == len(self.arrChars):
                self.arrChars.append(value)
            else:
                self.arrChars[address] = value
            return 
        elif address >= 7000 and address <= 7999:
            address = address - 7000
            if address == len(self.tempInts):
                self.tempInts.append(value)
            else:
                self.tempInts[address] = value
            return 
        elif address >= 8000 and address <= 8999:
            address = address - 8000
            if address == len(self.tempFloats):
                self.tempFloats.append(value)
            else:
                self.tempFloats[address] = value
            return 
        elif address >= 9000 and address <= 9999:
            address = address - 9000
            if address == len(self.tempChars):
                self.tempChars.append(value)
            else:
                self.tempChars[address] = value
            return 
        elif address >= 10000 and address <= 10999:
            address = address - 10000
            if address == len(self.constInts):
                self.constInts.append(value)
            else:
                self.constInts[address] = value
            return 
        elif address >= 11000 and address <= 11999:
            address = address - 11000
            if address == len(self.constFloats):
                self.constFloats.append(value)
            else:
                self.constFloats[address] = value
            return 
        elif address >= 12000 and address <= 12999:
            address = address - 12000
            if address == len(self.constChars):
                self.constChars.append(value)
            else:
                self.constChars[address] = value
            return 
        elif address >= 13000 and address <= 13999:
            address = address - 13000
            if address == len(self.voidfunctions):
                self.voidfunctions.append(value)
            else:
                self.voidfunctions[address] = value
            return
        else:
            raise MemoryError
    def printMem(self):
        print(self.arrInts)
        print(self.arrFloats)
        print(self.arrChars)
        print(self.tempInts)
        print(self.tempFloats)
        print(self.tempChars)
        print(self.constInts)
        print(self.constFloats)
        print(self.constChars)
        print(self.voidfunctions)
# memory_table = Stack()
# local_memory_stack = Stack()
global_memory = GlobalMemory()
local_memory_stack = Stack()

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
    return (address >= 4000 and address < 7000) or (address >= 14000 and address < 17000)

def getValue(address):
    if isLocal(address):
        return local_memory_stack.top().getValue(address)
    else:
        return global_memory.getValue(address)
def setValue(address, value):
    if isLocal(address):
        return local_memory_stack.top().setValue(address,value)
    else:
        return global_memory.setValue(address,value)
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