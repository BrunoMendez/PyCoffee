# Bruno Mendez A01194018
# Esteban Torres A01193925

# Main document for compilation.
# In this code we verify that the grammar is correct and that all the tokens
# are in the right place. Otherwise we would generate a syntax error
# if the submitted code does not comply with the grammar or
# an Illegal Character error is thrown if an unknown character is used

import ply.yacc as yacc
import lexer
from errors import *
from datastructures import *
import memory
from constants import *
import vm

# Importar tokens list
tokens = lexer.tokens

# Import flask libraries for backend.
from flask import *
from flask_cors import CORS

# Definition of global variables used in compilation.

# Dictionaries used for memory in compilation
functionDirectory = {}
variableTable = {}
paramTable = {}

# Stacks used in compilation
operatorStack = Stack()
operandStack = Stack()
typeStack = Stack()
jumpStack = Stack()

# List of generated quadruples.
quadruples = []

# Global strings to check the state of the compiler.
currentScope = GLOBAL_SCOPE
currentType = ""
function_id = ""
function_type = ""

# Fila para agregar variables en orden.
varIds = Queue()

# Checks if the variable is a function
checkFunction = False

# Checks if the function has a return statement.
hasReturn = False

# Counts the parameters of the function to call
paramCounter = 0


# This function returns a string that tells us in which range of addresses in
# memory the variable must be.
#
# Receives the variable type and scope (global or local) as parameters.
def convert_type(idType, scope):
    if idType == VOID:
        return VOID
    if scope == GLOBAL_SCOPE:
        if idType == INT:
            return GLOBAL_INT
        if idType == FLOAT:
            return GLOBAL_FLOAT
        if idType == CHAR:
            return GLOBAL_CHAR
    if scope == LOCAL_SCOPE:
        if idType == INT:
            return LOCAL_INT
        if idType == FLOAT:
            return LOCAL_FLOAT
        if idType == CHAR:
            return LOCAL_CHAR
    if scope == TEMPORAL_SCOPE and currentScope == GLOBAL_SCOPE:
        if idType == INT:
            return TEMPORAL_INT
        if idType == FLOAT:
            return TEMPORAL_FLOAT
        if idType == CHAR:
            return TEMPORAL_CHAR

    if scope == TEMPORAL_SCOPE and currentScope != GLOBAL_SCOPE:
        if idType == INT:
            return TEMPORAL_LOCAL_INT
        if idType == FLOAT:
            return TEMPORAL_LOCAL_FLOAT
        if idType == CHAR:
            return TEMPORAL_LOCAL_CHAR
    raise InvalidType


# The token '(' takes precedence over the id to avoid shift reduce conflicts.
precedence = (
    ('right', 'ID'),
    ('nonassoc', 'LPAREN'),
)


# Definition of the code's structure.
def p_program(p):
    'program : PROGRAM ID createGlobalTables SEMICOLON vars functions MAIN LPAREN RPAREN mainStart block'
    # Last quadruple that indicates the end of the code.
    endQuad = Quadruple(END_PROG, None, None, None)
    quadruples.append(endQuad)

    # Prints the final state of the compiler.
    print(variableTable)
    print(functionDirectory)
    for quadruple in quadruples:
        print(quadruple)
    print(paramTable)
    print("Type stack: ", typeStack)
    print("Operand stack: ", operandStack)


# Indicates the position of the main function.
def p_mainStart(p):
    'mainStart :'
    quadruples[0].result = len(quadruples)
    functionDirectory[GLOBAL_SCOPE][FUNCTION_QUAD_INDEX] = len(quadruples)


# Initializes the global variables and dictionaries and generates the Goto Main Quadruple
def p_createGlobalTables(p):
    'createGlobalTables : '
    currentScope = GLOBAL_SCOPE
    functionDirectory[currentScope] = {
        TYPE: VOID,
        FUNCTION_PARAM_COUNT: 0,
        FUNCTION_VAR_COUNT: 0,
        FUNCTION_QUAD_INDEX: 0,
        FUNCTION_TEMP_COUNT: 0
    }
    variableTable[currentScope] = {}
    quad = Quadruple(GOTO, MAIN, None, None)
    quadruples.append(quad)


def p_vars(p):
    '''vars : VAR varsPrime 
            | '''


def p_varsPrime(p):
    '''varsPrime : listIds COLON type addVars SEMICOLON varsPrime 
                | '''


# Adds the variables in the queue to the variable table.
def p_addVars(p):
    'addVars :'
    while not varIds.empty():
        var = varIds.dequeue()
        ## Checks if the variable is an array.
        if (type(var) is dict):
            if (var[ID] in variableTable[currentScope]):
                raise VarAlreadyInTable
            address = ""
            # Gets the base address of the array.
            if (currentScope == GLOBAL_SCOPE):
                address = memory.getNextAddress(convert_type(
                    currentType, GLOBAL_SCOPE),
                                                offset=var[R])
            else:
                address = memory.getNextAddress(convert_type(
                    currentType, LOCAL_SCOPE),
                                                offset=var[R])
            # Populates the variable table entry of the array.
            variableTable[currentScope][var[ID]] = {
                TYPE: currentType,
                ADDRESS: address,
                IS_ARRAY: True,
                # 1 or 2 dimensions
                DIM: var[DIM],
                SIZE: var[R],
                # limit of first dimension.
                LIM: var[LIM],
            }
            # If its a matrix add the limit of the second dimension.
            if (var[DIM] > 1):
                variableTable[currentScope][var[ID]][LIM2] = var[LIM2]
        # If it's not an array
        else:
            if (var in variableTable[currentScope]):
                raise VarAlreadyInTable
            address = ""

            # Get variable address and populate variable table.
            if (currentScope == GLOBAL_SCOPE):
                address = memory.getNextAddress(
                    convert_type(currentType, GLOBAL_SCOPE))
            else:
                address = memory.getNextAddress(
                    convert_type(currentType, LOCAL_SCOPE))
            variableTable[currentScope][var] = {
                TYPE: currentType,
                ADDRESS: address,
                IS_ARRAY: False
            }


# TODO: Checar si vale la pena pasar arrays como parametros.
# Adds local function variables to variable table.
# same logic as addVars but with a paramTable.
def p_addFunction2(p):
    'addFunction2 :'
    while not varIds.empty():
        var = varIds.dequeue()
        if (var in variableTable[currentScope]):
            raise VarAlreadyInTable
        else:
            variableTable[currentScope][var] = {
                TYPE:
                currentType,
                ADDRESS:
                memory.getNextAddress(convert_type(currentType, LOCAL_SCOPE)),
                IS_ARRAY:
                False
            }
            # Populates param table so that we know what parameters each function takes.
            paramTable[currentScope][var] = {TYPE: currentType}


def p_functions(p):
    '''functions : function functions
                | '''


def p_listIds(p):
    '''listIds : ids listIdsPrime'''


def p_listIdsPrime(p):
    '''listIdsPrime : COMA ids listIdsPrime 
                    | '''


def p_ids(p):
    '''ids : ID addId
            | ID addId LBRACKET CST_INT addArr1 RBRACKET
            | ID addId LBRACKET CST_INT addArr1 RBRACKET LBRACKET CST_INT addArr2 RBRACKET'''


# Adds array with data to varIDs queue
def p_addArr1(p):
    'addArr1 :'
    id = varIds.back()
    # Sets first dimension limit to CST_INT passed
    array = {ID: id, DIM: 1, LIM: int(p[-1])}
    # Sets size to first dimension limit.
    array[R] = array[LIM]
    # Pass array as dict to diferentiate arrays and variables.
    varIds.enqueue(array)


def p_addArr2(p):
    'addArr2 :'
    array = varIds.back()
    # Adds a second dimension
    array[DIM] += 1
    array[LIM2] = int(p[-1])
    # Set size to first dimension * second dimension.
    array[R] = array[LIM2] * array[R]
    # Pass array as dict to diferentiate arrays and variables.
    varIds.enqueue(array)


# Adds variable id to queue.
def p_addId(p):
    'addId :'
    varIds.enqueue(p[-1])


# Checks if ID is not a function ID.
def p_checkIfNotFunction(p):
    'checkIfNotFunction :'
    if checkFunction:
        raise VarNotDefined


# Used for variable operations that don't support functions. (assignment, read...)
def p_ids2(p):
    '''ids2 : ID addIdToStack checkIfNotFunction
            | ID addIdToStack arrPos'''


# Gets Id address and type and adds it to operator stack and type stack.
def p_addIdToStack(p):
    'addIdToStack :'
    # manejar arrays
    varId = p[-1]
    if varId in functionDirectory:
        # Marks ID as function ID.
        global checkFunction
        checkFunction = True
        typeStack.push(functionDirectory[varId][TYPE])
        operandStack.push(varId)
    # Checks if var is local first.
    elif (varId in variableTable[currentScope]):
        varType = variableTable[currentScope][varId][TYPE]
        typeStack.push(varType)
        # If var is array push array ID instead of address.
        if (variableTable[currentScope][varId][IS_ARRAY]):
            operandStack.push(variableTable[currentScope][varId])
        else:
            operandStack.push(variableTable[currentScope][varId][ADDRESS])
    # Then check global variables.
    elif (varId in variableTable[GLOBAL_SCOPE]):
        varType = variableTable[GLOBAL_SCOPE][varId][TYPE]
        typeStack.push(varType)
        # If var is array push array ID instead of address.
        if (variableTable[GLOBAL_SCOPE][varId][IS_ARRAY]):
            operandStack.push(variableTable[GLOBAL_SCOPE][varId])
        else:
            operandStack.push(variableTable[GLOBAL_SCOPE][varId][ADDRESS])
    else:
        raise VarNotDefined


def p_arrPos(p):
    '''arrPos : LBRACKET getArr1 exp getArr2 RBRACKET getArr5
                | LBRACKET getArr1 exp getArr2 RBRACKET LBRACKET getArr3 exp getArr4 RBRACKET getArr5'''

# Gets the id of an array and push a verify operation in an array [1st dimension]
# Pushes a fake botton
def p_getArr1(p):
    'getArr1 :'
    arrId = operandStack.top()
    # Verifies that id stored in the Stack is a dictionary of an array
    if isinstance(arrId, dict):
        if IS_ARRAY in arrId.keys():
            if arrId[IS_ARRAY]:
                operatorStack.push(VERIFY_ARR)
                # Serves to check that the size matches the size of the declared array
                # Of the first dimension
                operatorStack.push("+")
                # Push a Fake bottom to the operatorStack
                operatorStack.push("%")
            else:
                raise TypeMismatchError
        else:
            raise TypeMismatchError
    else:
        raise TypeMismatchError

# Gets the id of an array and push a verify operation in an array [2nd dimension]
def p_getArr3(p):
    'getArr3 :'
    operatorStack.push(VERIFY_ARR)
    # Serves to check that the size matches the size of the declared array
    # Of the second dimension
    operatorStack.push("+")
    # Push a Fake bottom to the operatorStack
    operatorStack.push("%")

# Calculates addresses if its a dimension=1 or dimension=2
# Gets the memory addresses of the indexes
# Checks that the value passed is an Integer
def p_getArr2(p):
    'getArr2 :'
    # pop fake bottom
    operatorStack.pop()
    # Pop the sum operator
    sumOp = operatorStack.pop()
    # Pop the verify operator
    verifyOp = operatorStack.pop()
    expResult = operandStack.pop()
    expType = typeStack.pop()
    arrId = operandStack.top()
    # Verifies that the number passed is an integer
    if expType == INT:
        quad = Quadruple(verifyOp, expResult, arrId[LIM], None)
        quadruples.append(quad)
        # If it is a 2-dimension array it calculates lim2*S1
        if arrId[DIM] == 2:
            sumOp = '*'
            operand = LIM2
        # If it is a 1-dimension array it calculates AddressB+S1
        else:
            operand = ADDRESS
        # get the memory address of the array id
        assignResult = memory.getNextAddress(CONSTANT_INT,
                                             value=arrId[operand],
                                             valType=INT)
        # get the memory address of the indexes
        result = memory.getNextAddress(convert_type(INT, TEMPORAL_SCOPE))
        quad = Quadruple(sumOp, expResult, assignResult, result)
        quadruples.append(quad)
        operandStack.push(result)
        typeStack.push(INT)
    else:
        raise TypeMismatchError

# Pop fake bottom and verifies that the value passed is not out of bounds
# Append quadruples of the addreses of the array/matrix
def p_getArr4(p):
    'getArr4 :'
    # Pop fake bottom
    operatorStack.pop()
    sumOp = operatorStack.pop()
    verifyOp = operatorStack.pop()
    expResult = operandStack.pop()
    expType = typeStack.pop()
    prevResult = operandStack.pop()
    typeStack.pop()
    if expType == INT:
        arrId = operandStack.top()
        baseAddress = memory.getNextAddress(CONSTANT_INT,
                                            value=arrId[ADDRESS],
                                            valType=INT)
        # Verifies that it is not out of bounds
        quad = Quadruple(verifyOp, expResult, arrId[LIM2], None)
        quadruples.append(quad)
        # S2 + S1*LIM2
        result = memory.getNextAddress(convert_type(INT, TEMPORAL_SCOPE))
        quad = Quadruple(sumOp, expResult, prevResult, result)
        quadruples.append(quad)
        address_result = memory.getNextAddress(
            convert_type(INT, TEMPORAL_SCOPE))
        # (S2 + S1*Lim2) + baseAddress
        quad = Quadruple(sumOp, result, baseAddress, address_result)
        quadruples.append(quad)
        operandStack.push(address_result)
        typeStack.push(INT)
    else:
        raise TypeMismatchError

# Push a fake bottom in the addres to delimit that from that point until pop of fake bottom
# is part of the array/matrix
def p_getArr5(p):
    'getArr5 :'
    address = operandStack.pop()
    addressType = typeStack.pop()
    arrId = operandStack.pop()
    arrType = typeStack.pop()
    # Cambiar a pointer
    address = "(" + str(address)
    operandStack.push(address)
    typeStack.push(arrType)

# Sets global currentType variable to the one passed
def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''
    global currentType
    currentType = p[1]

# Sets the type of the awaited return .. in this case its void therefore -- no return is expected--
def p_returnType(p):
    '''returnType : type
                    | VOID'''
    if (p[1] == VOID):
        global currentType
        currentType = p[1]

# Gets the currentScope of the program, when finished running a function
# Resets Memory's LocalTemporals and Locals
# Deletes variableTable of the currentScope == function
# sets the currentScope of the program to Global
# if a non void function is declared checks if return is present else push EndFunc quadruple
def p_function(p):
    'function : returnType FUNCTION ID addFunction1 LPAREN params RPAREN addFunction3 vars addFunction4 block'
    global currentScope
    functionDirectory[currentScope][
        FUNCTION_TEMP_COUNT] = memory.resetLocalTemporals()
    functionDirectory[currentScope][FUNCTION_VAR_COUNT] = memory.resetLocals()
    del variableTable[currentScope]
    currentScope = GLOBAL_SCOPE
    if (function_type != VOID and (not hasReturn)):
        raise NonVoidFuncReturnMissing
    quadruples.append(Quadruple(END_FUNC, None, None, None))

# Sets the index of the quadruples length (at the moment) for the functionDirectory
def p_addFunction4(p):
    'addFunction4 :'
    functionDirectory[currentScope][FUNCTION_QUAD_INDEX] = len(quadruples)

# Sets the parameters count for the functionDirectory
def p_addFunction3(p):
    'addFunction3 :'
    functionDirectory[currentScope][FUNCTION_PARAM_COUNT] = len(
        paramTable[currentScope])

# Initialize dictionaries, booleans. Sanity checks and delimits the function’s information
def p_addFunction1(p):
    'addFunction1 :'
    global hasReturn
    global currentScope
    global function_id
    global function_type
    # Initialize hasReturn boolean to False, to later check if void or non void
    hasReturn = False
    # gets the currentScope of the program
    currentScope = p[-1]
     # Initialize the paramTable of the currentScope to an empty dictionary
    paramTable[currentScope] = {}
    # Initialize the functionDirectory of the currentScope to an empty dictionary
    functionDirectory[currentScope] = {}
    # Sets the Type of the functionDirectory of the currentScope
    functionDirectory[currentScope][TYPE] = currentType
    # Sets the memory address of the functionDirectory of the currentScope
    functionDirectory[currentScope][ADDRESS] = memory.getNextAddress(
        convert_type(currentType, GLOBAL_SCOPE))
    # Sets the variableTable of the currentScope to an empty dictionary
    variableTable[currentScope] = {}
    function_id = currentScope
    function_type = currentType
    if (function_type != VOID):
        # Check if the variable is already declared in the global scope
        if (function_id in variableTable[GLOBAL_SCOPE]):
            raise VarAlreadyInTable
        # Sets the function in the variableTable of the global scope and delimits is not an array
        variableTable[GLOBAL_SCOPE][function_id] = {
            TYPE:
            function_type,
            ADDRESS:
            memory.getNextAddress(convert_type(function_type, GLOBAL_SCOPE)),
            IS_ARRAY:
            False
        }


def p_params(p):
    '''params : ids COLON type addFunction2 paramsPrime
            |'''


def p_paramsPrime(p):
    '''paramsPrime : COMA params 
                | '''


def p_block(p):
    '''block : LBRACE statements RBRACE'''


def p_statements(p):
    '''statements : statement statements 
                | '''


def p_statement(p):
    '''statement : assignment
                | write
                | callVoidF
                | return
                | read
                | decision
                | repetition
                | expression'''


def p_assignment(p):
    'assignment : ids2 EQUAL addOperator expression addAssignment SEMICOLON'


def p_write(p):
    '''write : PRINT LPAREN writePrime RPAREN SEMICOLON'''


def p_writePrime(p):
    '''writePrime : addFakeBottom expression popOperator printExpression writePrimePrime
                    | CST_STRING printString writePrimePrime'''

# Helps to print expressions
# e.g. print(x);
def p_printExpression(p):
    'printExpression :'
    typeStack.pop()
    quadruple = Quadruple(PRINT_EXP, None, None, operandStack.pop())
    quadruples.append(quadruple)

# Helps to print signs
# e.g. print("Hello World");
def p_printString(p):
    'printString :'
    quadruple = Quadruple(PRINT_STR, None, None, p[-1])
    quadruples.append(quadruple)

# Pop operator of the operatorStack
def p_popOperator(p):
    'popOperator :'
    operatorStack.pop()

# Add fake bottom to the operatorStack
def p_addFakeBottom(p):
    'addFakeBottom :'
    operatorStack.push("$")


def p_writePrimePrime(p):
    '''writePrimePrime : COMA writePrime
                        | '''


def p_callVoidF(p):
    'callVoidF : ID addIdToStack callFunction SEMICOLON'


def p_callFunction(p):
    '''callFunction : LPAREN callFunction1 expressions RPAREN callFunction3'''

# Checks that the variable is a function, reset the boolean and push a Fake bottom
# Sets the paramCounter to 0 --> This helps for functions without parameters
def p_callFunction1(p):
    'callFunction1 :'
    global checkFunction
    if checkFunction:
        checkFunction = False
        function_id = operandStack.top()
        operatorStack.push("{")
        # Push ERA quadruple with its memory
        quad = Quadruple(ERA, functionDirectory[function_id][ADDRESS], None,
                         None)
        # Appends it to the quadruples list
        quadruples.append(quad)
        global paramCounter
        paramCounter = 0
    else:
        raise FunctionNotDeclared

# Counts the parameters of the function and set the Parameter quadruple with its argument and paramCounter
# Checks that the parameter number matches the parameters passed and also that it matches its type
def p_callFunction2(p):
    'callFunction2 :'
    global paramCounter
    paramCounter += 1
    argument = operandStack.pop()
    argumentType = typeStack.pop()
    function_id = operandStack.top()
    if paramCounter == len(paramTable[function_id]):
        keys_list = list(paramTable[function_id])
        key = keys_list[paramCounter - 1]
        print(paramTable)
        if argumentType == paramTable[function_id][key][TYPE]:
            quad = Quadruple(PARAMETER, argument, None, paramCounter - 1)
            quadruples.append(quad)
        else:
            raise TypeMismatchError
    else:
        raise InvalidParamNum


def p_callFunction3(p):
    'callFunction3 :'
    global paramCounter
    function_id = operandStack.pop()
    operatorStack.pop()
    idType = typeStack.pop()
    print(paramCounter)
    if paramCounter == len(paramTable[function_id]):
        result = memory.getNextAddress(convert_type(idType, TEMPORAL_SCOPE))
        quad = Quadruple(GOSUB, functionDirectory[function_id][ADDRESS], None,
                         functionDirectory[function_id][FUNCTION_QUAD_INDEX])
        quadruples.append(quad)
        if functionDirectory[function_id][TYPE] != VOID:
            assignQuad = Quadruple('=',
                                   functionDirectory[function_id][ADDRESS],
                                   None, result)
            quadruples.append(assignQuad)
            operandStack.push(result)
            typeStack.push(functionDirectory[function_id][TYPE])
    else:
        raise InvalidParamNum


def p_expressions(p):
    '''expressions : expression callFunction2 expressionsPrime 
                |'''


def p_expressionsPrime(p):
    '''expressionsPrime : COMA expressions 
                        |'''


def p_return(p):
    'return : RETURN LPAREN expression RPAREN SEMICOLON'
    global hasReturn
    hasReturn = True
    result = operandStack.pop()
    res_type = typeStack.pop()
    if (res_type != variableTable[GLOBAL_SCOPE][function_id][TYPE]):
        raise TypeMismatchError
    else:
        quadruple = Quadruple(RETURN, None, None, result)
        quadruples.append(quadruple)


def p_read(p):
    'read : INPUT addOperator LPAREN readPrime RPAREN SEMICOLON'


def p_readPrime(p):
    'readPrime : ids2 readVar readPrimePrime'


def p_readVar(p):
    'readVar :'
    operatorStack.pop()
    var = operandStack.pop()
    varType = typeStack.pop()
    quadruple = Quadruple(INPUT, varType, None, var)
    quadruples.append(quadruple)


def p_readPrimePrime(p):
    '''readPrimePrime : COMA readPrime
                    | '''


def p_repetition(p):
    '''repetition : conditional
                    | nonConditional'''


def p_decision(p):
    'decision : IF LPAREN expression addIf1 RPAREN block decisionPrime addIf2'


def p_decisionPrime(p):
    '''decisionPrime : addIf3 ELSE block
                    |'''


def p_conditional(p):
    'conditional : WHILE addWhile1 LPAREN expression addWhile2 RPAREN block addWhile3'


# Podrias inicializar el for con una funcion?
def p_nonConditional(p):
    'nonConditional : FOR LPAREN ids2 EQUAL addOperator exp addFor1 COLON exp addFor2 RPAREN block addFor3'


def p_expression(p):
    '''expression : miniExpression addAndOr AND addOperator expression
                    | miniExpression addAndOr OR addOperator expression
                    | miniExpression addAndOr'''


def p_miniExpression(p):
    '''miniExpression : NOT addOperator LPAREN expression RPAREN addNot
                    | microExpression addNot'''


def p_microExpression(p):
    '''microExpression : exp addExp GT addOperator microExpression
                | exp addExp LT addOperator microExpression
                | exp addExp NE addOperator microExpression
                | exp addExp EQEQ addOperator microExpression
                | exp addExp LTEQ addOperator microExpression
                | exp addExp GTEQ addOperator microExpression
                | exp addExp'''


def p_exp(p):
    '''exp : term addTerm
            | term addTerm PLUS addOperator exp
            | term addTerm MINUS addOperator exp'''


def p_term(p):
    '''term : factor addFactor
            | factor addFactor MULTIPLY addOperator term 
            | factor addFactor DIVIDE addOperator term'''


def p_factor(p):
    '''factor : LPAREN addOperator expression RPAREN popOperator
                | varCst'''


def p_varCst(p):
    '''varCst : CST_FLOAT addFloat
            | CST_INT addInt
            | CST_CHAR addChar
            | callableCst'''


def p_callableCst(p):
    '''callableCst : ID addIdToStack checkIfNotFunction
                |  ID addIdToStack callFunction
                | ID addIdToStack arrPos'''


def p_popOperator(p):
    'popOperator :'
    operatorStack.pop()


def p_addOperator(p):
    'addOperator :'
    operatorStack.push(p[-1])


def p_addAssignment(p):
    'addAssignment :'
    res = operandStack.pop()
    resType = typeStack.pop()
    leftSide = operandStack.pop()
    leftType = typeStack.pop()
    operator = operatorStack.pop()
    opType = semanticCube[(leftType, resType, operator)]
    if (opType != ERROR):
        # esto estaba asi -> Quadruple(operator, None, res, leftSide)
        quadruple = Quadruple(operator, res, None, leftSide)
        quadruples.append(quadruple)
    else:
        # Create error message
        raise TypeMismatchError


def p_addAndOr(p):
    'addAndOr :'
    if (operatorStack.top() in [AND, OR]):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = operandStack.pop()
        leftOperand = operandStack.pop()
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != ERROR:
            result = memory.getNextAddress(
                convert_type(resultType, TEMPORAL_SCOPE))
            quadruples.append(
                Quadruple(operator, leftOperand, rightOperand, result))
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
        else:
            raise TypeMismatchError()


def p_addNot(p):
    'addNot :'
    if (operatorStack.top() == NOT):
        operator = operatorStack.pop()
        opType = typeStack.pop()
        operand = operandStack.pop()
        if (opType == INT):
            result = memory.getNextAddress(convert_type(
                opType, TEMPORAL_SCOPE))
            quadruples.append(Quadruple(operator, operand, None, result))
            operandStack.push(result)
            typeStack.push(INT)
            # if any operand were a temporal space return it to avail
        else:
            raise TypeMismatchError()


def p_addExp(p):
    'addExp :'
    if (operatorStack.top() in ['<', '<=', '>', '>=', '<>', '==']):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = operandStack.pop()
        leftOperand = operandStack.pop()
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != ERROR:
            result = memory.getNextAddress(
                convert_type(resultType, TEMPORAL_SCOPE))
            quadruples.append(
                Quadruple(operator, leftOperand, rightOperand, result))
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
        else:
            raise TypeMismatchError()


def p_addTerm(p):
    'addTerm :'
    if (operatorStack.top() in ['+', '-']):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = operandStack.pop()
        leftOperand = operandStack.pop()
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != ERROR:
            result = memory.getNextAddress(
                convert_type(resultType, TEMPORAL_SCOPE))
            quadruple = Quadruple(operator, leftOperand, rightOperand, result)
            quadruples.append(quadruple)
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
        else:
            raise TypeMismatchError()


def p_addFactor(p):
    'addFactor :'
    if (operatorStack.top() in ['*', '/']):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = operandStack.pop()
        leftOperand = operandStack.pop()
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != ERROR:
            result = memory.getNextAddress(
                convert_type(resultType, TEMPORAL_SCOPE))
            quadruple = Quadruple(operator, leftOperand, rightOperand, result)
            quadruples.append(quadruple)
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
        else:
            # error('type mismatch')
            raise TypeMismatchError()


def p_addIf1(p):
    'addIf1 : '
    exp_type = typeStack.pop()
    result = operandStack.pop()
    if exp_type != INT:
        raise TypeMismatchError
    else:
        quadruple = Quadruple(GOTOF, result, None, None)
        quadruples.append(quadruple)
        jumpStack.push(len(quadruples) - 1)


def p_addIf2(p):
    'addIf2 : '
    end = jumpStack.pop()
    quadruples[end] = Quadruple(quadruples[end].operator,
                                quadruples[end].leftOperand, None,
                                len(quadruples))


def p_addIf3(p):
    'addIf3 : '
    false = jumpStack.pop()
    quadruple = Quadruple(GOTO, None, None, None)
    quadruples.append(quadruple)
    jumpStack.push(len(quadruples) - 1)
    quadruples[false] = Quadruple(GOTOF, quadruples[false].leftOperand, None,
                                  len(quadruples))


def p_addWhile1(p):
    'addWhile1 : '
    jumpStack.push(len(quadruples))


def p_addWhile2(p):
    'addWhile2 : '
    result = operandStack.pop()
    exp_type = typeStack.pop()
    if (exp_type != INT):
        # Logica de manejo de errors
        raise TypeMismatchError
    else:
        quadruple = Quadruple(GOTOF, result, None, None)
        quadruples.append(quadruple)
        jumpStack.push(len(quadruples) - 1)


def p_addWhile3(p):
    'addWhile3 : '
    end = jumpStack.pop()
    ret = jumpStack.pop()
    quadruple = Quadruple(GOTO, None, None, ret)
    quadruples.append(quadruple)
    quadruples[end] = Quadruple(quadruples[end].operator,
                                quadruples[end].leftOperand, None,
                                len(quadruples))


def p_addFor1(p):
    'addFor1 :'
    res = operandStack.pop()
    resType = typeStack.pop()
    leftSide = operandStack.pop()
    leftType = typeStack.pop()
    operator = operatorStack.pop()
    if (resType == INT and leftType == INT):
        quadruple = Quadruple(operator, res, None, leftSide)
        quadruples.append(quadruple)
        # Preparacion para hacer la suma a la variable cuando acabe el for
        operandStack.push(leftSide)
        typeStack.push(leftType)
        operatorStack.push('+')
        # Fake bottom
        operatorStack.push("#")
        # Preparacion para hacer la comparacion aver si entra al for
        operandStack.push(leftSide)
        typeStack.push(leftType)
        operatorStack.push('<=')
        # Fake bottom
        operatorStack.push("%")
    else:
        # Error for loops must be ints
        raise TypeMismatchError


def p_addFor2(p):
    'addFor2 :'
    # Pop fake bottom
    fake_bottom = operatorStack.pop()
    print("Fake_bottom", fake_bottom)
    # Get <= operator
    operator = operatorStack.pop()
    # Get Types and operands
    rightType = typeStack.pop()
    leftType = typeStack.pop()
    rightOperand = operandStack.pop()
    leftOperand = operandStack.pop()
    if rightType == INT and leftType == INT:
        result = memory.getNextAddress(TEMPORAL_INT)
        quadruples.append(
            Quadruple(operator, leftOperand, rightOperand, result))
        jumpStack.push(len(quadruples) - 1)
        quadrupleGotoF = Quadruple(GOTOF, result, None, None)
        quadruples.append(quadrupleGotoF)
        jumpStack.push(len(quadruples) - 1)
        # if any operand were a temporal space return it to avail
    else:
        # Error for loops must be ints
        raise TypeMismatchError


def p_addFor3(p):
    'addFor3 :'
    # Pop fake bottom
    fake_bottom = operatorStack.pop()
    print("Fake bottom", fake_bottom)
    # Get sum operator
    operator = operatorStack.pop()
    leftSide = operandStack.pop()
    leftType = typeStack.pop()
    rightSide = memory.getNextAddress(CONSTANT_INT, value='1', valType=INT)
    rightType = INT
    resultType = semanticCube[(leftType, rightType, operator)]
    print("Addfor3", leftSide, rightSide)
    if leftType == INT:
        result = memory.getNextAddress(convert_type(resultType,
                                                    TEMPORAL_SCOPE))
        quadruple = Quadruple(operator, leftSide, rightSide, result)
        quadruples.append(quadruple)
        quadrupleAssign = Quadruple('=', result, None, leftSide)
        quadruples.append(quadrupleAssign)

        end = jumpStack.pop()
        ret = jumpStack.pop()
        quadruple = Quadruple(GOTO, None, None, ret)
        quadruples.append(quadruple)
        quadruples[end] = Quadruple(quadruples[end].operator,
                                    quadruples[end].leftOperand, None,
                                    len(quadruples))
    else:
        # error for loops must be ints
        raise TypeMismatchError


# getConvertedOperant is not necessary now!
def p_addFloat(p):
    'addFloat :'
    address = memory.getNextAddress(CONSTANT_FLOAT, value=p[-1], valType=FLOAT)
    operandStack.push(address)
    typeStack.push(FLOAT)


def p_addInt(p):
    'addInt :'
    address = memory.getNextAddress(CONSTANT_INT, value=p[-1], valType=INT)
    operandStack.push(address)
    typeStack.push(INT)


def p_addChar(p):
    'addChar :'
    address = memory.getNextAddress(CONSTANT_CHAR, value=p[-1], valType=CHAR)
    operandStack.push(address)
    typeStack.push(CHAR)


# Manejo de errores
def p_error(p):
    error = ("Syntax error at line %d, token=%s, value=%s col=%s" %
             (p.lineno, p.type, p.value, p.lexpos))
    print(error)
    raise CustomSyntaxError(error)


def initAll():
    global currentScope
    global quadruples
    global functionDirectory
    global variableTable
    global paramTable
    global varIds
    global currentType
    global checkFunction
    global hasReturn
    global paramCounter
    global operatorStack
    global operandStack
    global typeStack
    global jumpStack
    global function_id
    global function_type
    currentScope = GLOBAL_SCOPE
    functionDirectory = {}
    variableTable = {}
    paramTable = {}
    varIds = Queue()
    currentType = ""
    checkFunction = False
    hasReturn = False
    paramCounter = 0
    operatorStack = Stack()
    operandStack = Stack()
    typeStack = Stack()
    jumpStack = Stack()
    quadruples = []
    function_id = ""
    function_type = ""
    memory.memory_table = {}
    memory.resetAll()


# Constructor del parser
parser = yacc.yacc()
# parsear archivo
app = Flask(__name__)
CORS(app)


@app.route('/')
def root():
    return "Hello World"


@app.route('/compile', methods=["POST"])
def compile():
    content = request.get_json()
    initAll()
    # Here we will pass to the vm
    # and return the result of the vm to the front
    try:
        parser.parse(content['codigo'])
        return vm.start(quadruples)
    except Exception as e:
        print("Error", e)
        errors = {1: "Error: " + str(e)}
        return errors


@app.route('/user-input', methods=["POST"])
def userInput():
    content = request.get_json()
    try:
        return vm.start(quadruples,
                        currentQuad=content[CURRENT_QUAD],
                        inputValue=content[INPUT_VALUE])
    except Exception as e:
        print("Error", e)
        errors = {1: "Error: " + str(e)}
        return errors


if __name__ == "__main__":
    app.run(host='0.0.0.0')
