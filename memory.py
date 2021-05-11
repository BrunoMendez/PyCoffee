GLOBAL_INT = 'gInt'
GLOBAL_FLOAT = 'gFloat'
GLOBAL_CHAR = 'gChar'
LOCAL_INT = 'lInt'
LOCAL_FLOAT = 'lFloat'
LOCAL_CHAR = 'lChar'
TEMPORAL_INT = 'tInt' 
TEMPORAL_FLOAT = 'tFloat'
TEMPORAL_CHAR = 'tChar'
CONSTANT_INT = 'cInt'
CONSTANT_FLOAT = 'cFloat'
CONSTANT_CHAR = 'cChar'
VOID = 'void'

types = {
    GLOBAL_INT : 1000,
    GLOBAL_FLOAT : 2000,
    GLOBAL_CHAR: 3000,
    LOCAL_INT: 5000,
    LOCAL_FLOAT : 4000,
    LOCAL_CHAR : 6000,
    TEMPORAL_INT : 7000,
    TEMPORAL_FLOAT : 8000,
    TEMPORAL_CHAR : 9000,
    CONSTANT_INT : 10000,
    CONSTANT_FLOAT : 11000,
    CONSTANT_CHAR : 12000,
    VOID : 13000
}

def getNextAddress(mem):
    types[mem] = types[mem] + 1
    if types[mem] % 1000 != 0:
        return types[mem] - 1
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