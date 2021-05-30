from constants import *
from datastructures import Queue, Stack
from errors import *
# Initalize types dictionary with their starting addresses in memory
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
    TEMPORAL_LOCAL_CHAR: 16000,
    POINTER: 17000
}


# LocalMemory Class to manage memory in functions
class LocalMemory():
    def __init__(self):
        self.memory = {}
        # Queue to manage parameters positions in memory regarding its type
        self.paramInts = Queue()
        self.paramFloats = Queue()
        self.paramChars = Queue()

    # function to get the value of the address
    def getValue(self, address):
        return self.memory[address]

    # function to set the value of the address
    def setValue(self, address, value):
        self.memory[address] = value

    # Function to print the memory
    def printMem(self):
        print(self.memory)

    # Function to add parameters in the correct index of memory
    def paramHelper(self, valueAddress):
        value = getValue(valueAddress)
        valueType = getType(valueAddress)
        if valueType == INT:
            self.paramInts.enqueue(value)
        elif valueType == FLOAT:
            self.paramFloats.enqueue(value)
        elif valueType == CHAR:
            self.paramChars.enqueue(value)

    # Function to assign parameters to memory based on their index in the queue and their type
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


# GlobalMemory Class to manage global memory
class GlobalMemory():
    def __init__(self):
        self.memory = {}

    # function to get the value of the address
    def getValue(self, address):
        return self.memory[address]

    # function to set the value of the address
    def setValue(self, address, value):
        self.memory[address] = value

    # Function to print the memory
    def printMem(self):
        print(self.memory)


# Instantiate GlobalMemory
global_memory = GlobalMemory()
# Instantiate LocalMemoryStack
# We use a stack to manage recursive calls
# instance in top of stack will always be the current local memory
local_memory_stack = Stack()


# get the type of the addresses without its scope
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
    elif 17000 <= address <= 17999:
        return POINTER


# [Used in compile time]
# Returns next available address for a given variable type range
# If array offset will be array size
def getNextAddress(typeRange, offset=1, value=None, valType=None):
    # Stores current available address
    current_address = types[typeRange]
    # May pass value and type to store constants from compilation
    if valType != None and value != None:
        # parse value
        if valType == INT:
            value = int(value)
        elif valType == FLOAT:
            value = float(value)
        global_memory.setValue(current_address, value)
    # Updates next available address
    types[typeRange] = types[typeRange] + offset
    # Checks that memory addresses are not overflowed
    if types[typeRange] % 1000 != 0:
        return current_address
    else:
        # StackOverflow error
        raise StackOverflow


# Function to check if its a local address
def isLocal(address):
    return (address >= 4000 and address < 7000) or (address >= 14000
                                                    and address < 17000)


# Returns value from current local memory/global memory
def getValue(address):
    # If pointer then get real address first
    if getType(address) == POINTER:
        address = global_memory.getValue(address)
    if isLocal(address):
        return local_memory_stack.top().getValue(address)
    else:
        return global_memory.getValue(address)


# Sets value into current local memory/global memory for a given address
def setValue(address, value):
    if isLocal(address):
        local_memory_stack.top().setValue(address, value)
    else:
        global_memory.setValue(address, value)


# Resets Local Temporals variables
def resetLocalTemporals():
    countInt = types[TEMPORAL_LOCAL_INT] - 14000
    countFloat = types[TEMPORAL_LOCAL_FLOAT] - 15000
    countChar = types[TEMPORAL_LOCAL_CHAR] - 16000
    types[TEMPORAL_LOCAL_INT] = 14000
    types[TEMPORAL_LOCAL_FLOAT] = 15000
    types[TEMPORAL_LOCAL_CHAR] = 16000
    return [countInt, countFloat, countChar]


# Resets Local variables
def resetLocals():
    countInt = types[LOCAL_INT] - 4000
    countFloat = types[LOCAL_FLOAT] - 5000
    countChar = types[LOCAL_CHAR] - 6000
    types[LOCAL_INT] = 4000
    types[LOCAL_FLOAT] = 5000
    types[LOCAL_CHAR] = 6000
    return [countInt, countFloat, countChar]


# Reset global and local memory
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
        TEMPORAL_LOCAL_CHAR: 16000,
        POINTER: 17000
    }
    global_memory = GlobalMemory()
    while (not local_memory_stack.empty()):
        local_memory_stack.pop()
