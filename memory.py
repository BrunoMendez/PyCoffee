from constants import *

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
    VOID: 13000
}

memory = {}


def getNextAddress(mem, offset=1, value=None, valType=None):
    current_address = types[mem]
    # parse value
    if valType == INT:
        value = int(value)
    elif valType == FLOAT:
        value = float(value)

    # if value store value
    if valType != None and value != None:
        memory[current_address] = value
    types[mem] = types[mem] + offset
    if types[mem] % 1000 != 0:
        return current_address
    else:
        raise MemoryError


def resetTemporals():
    count = 0
    count += types[TEMPORAL_INT] - 7000
    count += types[TEMPORAL_FLOAT] - 8000
    count += types[TEMPORAL_CHAR] - 9000
    types[TEMPORAL_INT] = 7000
    types[TEMPORAL_FLOAT] = 8000
    types[TEMPORAL_CHAR] = 9000
    return count


def resetLocals():
    count = 0
    count += types[LOCAL_INT] - 4000
    count += types[LOCAL_FLOAT] - 5000
    count += types[LOCAL_CHAR] - 6000
    types[LOCAL_INT] = 4000
    types[LOCAL_FLOAT] = 5000
    types[LOCAL_CHAR] = 6000
    return count


def resetAll():
    global types
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
        VOID: 13000
    }
