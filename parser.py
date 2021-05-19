# Bruno Mendez A01194018
# Esteban Torres A01193925
# bug report ----> si no especificas la variable arriba del programa se queda esperando y no arroja ningun resultado
# hacer algo para que si se pone una variable que no existe en la tabla regresar un error(variable not declared!)
# no estamos pasando el tipo de la variable al typeStack
from os import error, strerror
import ply.yacc as yacc
import sys
import lexer
from errors import *
from datastructures import *
from memory import *
from constants import *
import vm

tokens = lexer.tokens
from flask import Flask, request
from flask_cors import CORS
from flask import jsonify

currentScope = GLOBAL_SCOPE
functionDirectory = {}
variableTable = {}
paramTable = {}
varIds = Stack()
currentType = ""
checkFunction = False
hasReturn = False
paramCounter = 0
operatorStack = Stack()
operandStack = Stack()
typeStack = Stack()
jumpStack = Stack()
forStack = Stack()
quadruples = []
function_id = ""
function_type = ""
countRuns = 0


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
    if scope == TEMPORAL_SCOPE:
        if idType == INT:
            return TEMPORAL_INT
        if idType == FLOAT:
            return TEMPORAL_FLOAT
        if idType == CHAR:
            return TEMPORAL_CHAR
    raise InvalidType


# Toma precedencia ( sobre ID para no reducir ID cuando llamamos una funcion.
precedence = (
    ('right', 'ID'),
    ('nonassoc', 'LPAREN'),
)


# Definicion de reglas de la gramatica
def p_program(p):
    'program : PROGRAM ID createGlobalTables SEMICOLON vars functions MAIN LPAREN RPAREN mainStart block'
    functionDirectory[GLOBAL_SCOPE][FUNCTION_TEMP_COUNT] = resetTemporals()
    functionDirectory[GLOBAL_SCOPE][FUNCTION_VAR_COUNT] = len(
        variableTable[GLOBAL_SCOPE])
    endQuad = Quadruple(END_PROG, None, None, None)
    quadruples.append(endQuad)
    print(variableTable)
    print(functionDirectory)
    for quadruple in quadruples:
        print(quadruple)
    print(paramTable)
    print("Type stack: ", typeStack)
    print("Operand stack: ", operandStack)


def p_mainStart(p):
    'mainStart :'
    quadruples[0].result = len(quadruples)
    functionDirectory[GLOBAL_SCOPE][FUNCTION_QUAD_INDEX] = len(quadruples)


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


def p_addVars(p):
    'addVars :'
    while not varIds.empty():
        var = varIds.pop()
        ## Nos dice si es un array
        if (type(var) is dict):
            if (var[ID] in variableTable[currentScope]):
                raise VarAlreadyInTable
            address = ""
            if (currentScope == GLOBAL_SCOPE):
                address = getNextAddress(convert_type(currentType,
                                                      GLOBAL_SCOPE),
                                         offset=var[R])
            else:
                address = getNextAddress(convert_type(currentType,
                                                      LOCAL_SCOPE),
                                         offset=var[R])
            variableTable[currentScope][var[ID]] = {
                TYPE: currentType,
                ADDRESS: address,
                IS_ARRAY: True,
                DIM: var[DIM],
                SIZE: var[R],
                LIM: var[LIM],
                M1: var[M1]
            }
            if (var[DIM] > 1):
                variableTable[currentScope][var[ID]][LIM2] = var[LIM2]
                variableTable[currentScope][var[ID]][M2] = var[M2]
        else:
            if (var in variableTable[currentScope]):
                raise VarAlreadyInTable
            address = ""
            if (currentScope == GLOBAL_SCOPE):
                address = getNextAddress(
                    convert_type(currentType, GLOBAL_SCOPE))
            else:
                address = getNextAddress(convert_type(currentType,
                                                      LOCAL_SCOPE))
            variableTable[currentScope][var] = {
                TYPE: currentType,
                ADDRESS: address,
                IS_ARRAY: False
            }


def p_addFunction2(p):
    'addFunction2 :'
    while not varIds.empty():
        var = varIds.pop()
        if (var in variableTable[currentScope]):
            raise VarAlreadyInTable
        else:
            variableTable[currentScope][var] = {
                TYPE: currentType,
                ADDRESS: getNextAddress(convert_type(currentType,
                                                     LOCAL_SCOPE)),
                IS_ARRAY: False
            }
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
            | ID addId LBRACKET CST_INT addId1 RBRACKET
            | ID addId LBRACKET CST_INT addId1 RBRACKET LBRACKET CST_INT addId2 RBRACKET'''


def p_addId1(p):
    'addId1 :'
    id = varIds.pop()
    array = {ID: id, DIM: 1, LIM: int(p[-1])}
    array[R] = array[LIM]
    array[M1] = 1
    varIds.push(array)


def p_addId2(p):
    'addId2 :'
    array = varIds.pop()
    array[DIM] += 1
    array[LIM2] = int(p[-1])
    array[R] = array[LIM2] * array[R]
    array[M1] = array[LIM2]
    array[M2] = 1
    varIds.push(array)


def p_addId(p):
    'addId :'
    varIds.push(p[-1])


def p_checkIfNotFunction(p):
    'checkIfNotFunction :'
    if checkFunction:
        raise VarNotDefined


def p_ids2(p):
    '''ids2 : ID addIdToStack checkIfNotFunction
            | ID addIdToStack arrPos'''


def p_addIdToStack(p):
    'addIdToStack :'
    # manejar arrays
    varId = p[-1]
    if varId in functionDirectory:
        global checkFunction
        checkFunction = True
        typeStack.push(functionDirectory[varId][TYPE])
        operandStack.push(varId)
    elif (varId in variableTable[currentScope]):
        varType = variableTable[currentScope][varId][TYPE]
        typeStack.push(varType)
        # if (variableTable[currentScope][varId][IS_ARRAY]):
        #     operandStack.push(varId)
        # else:
        operandStack.push(variableTable[currentScope][varId][ADDRESS])
    elif (varId in variableTable[GLOBAL_SCOPE]):
        varType = variableTable[GLOBAL_SCOPE][varId][TYPE]
        typeStack.push(varType)
        # if (variableTable[currentScope][varId][IS_ARRAY]):
        #     operandStack.push(varId)
        # else:
        operandStack.push(variableTable[GLOBAL_SCOPE][varId][ADDRESS])
    else:
        raise VarNotDefined


def p_arrPos(p):
    '''arrPos : LBRACKET exp RBRACKET
                | LBRACKET exp RBRACKET LBRACKET exp RBRACKET'''


# def p_addArr1(p):
#     'addArr1 :'
#     operatorStack.push("(")

# def p_addArr2(p):
#     'addArr2 :'
#     exp = operandStack.pop()
#     exp_type = typeStack.pop()
#     id = operandStack.pop()
#     id_type = typeStack.pop()
#     Quadruple("<", exp,  )
#     print(exp, exp_type, id, id_type)


def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''
    global currentType
    currentType = p[1]


def p_returnType(p):
    '''returnType : type
                    | VOID'''
    if (p[1] == VOID):
        global currentType
        currentType = p[1]


def p_function(p):
    'function : returnType FUNCTION ID addFunction1 LPAREN params RPAREN addFunction3 vars addFunction4 block'
    global currentScope
    functionDirectory[currentScope][FUNCTION_TEMP_COUNT] = resetTemporals()
    functionDirectory[currentScope][FUNCTION_VAR_COUNT] = resetLocals()
    del variableTable[currentScope]
    currentScope = GLOBAL_SCOPE
    if (function_type != VOID and (not hasReturn)):
        raise NonVoidFuncReturnMissing
    elif not hasReturn and function_type == VOID:
        quadruples.append(Quadruple(END_FUNC, None, None, None))


def p_addFunction4(p):
    'addFunction4 :'
    functionDirectory[currentScope][FUNCTION_QUAD_INDEX] = len(quadruples)


def p_addFunction3(p):
    'addFunction3 :'
    functionDirectory[currentScope][FUNCTION_PARAM_COUNT] = len(
        paramTable[currentScope])


def p_addFunction1(p):
    'addFunction1 :'
    global hasReturn
    global currentScope
    global function_id
    global function_type
    hasReturn = False
    currentScope = p[-1]
    paramTable[currentScope] = {}
    functionDirectory[currentScope] = {}
    functionDirectory[currentScope][TYPE] = currentType
    functionDirectory[currentScope][ADDRESS] = getNextAddress(
        convert_type(currentType, GLOBAL_SCOPE))
    variableTable[currentScope] = {}
    function_id = currentScope
    function_type = currentType
    if (function_type != VOID):
        if (function_id in variableTable[GLOBAL_SCOPE]):
            raise VarAlreadyInTable
        variableTable[GLOBAL_SCOPE][function_id] = {
            TYPE: function_type,
            ADDRESS: getNextAddress(convert_type(function_type, GLOBAL_SCOPE)),
            IS_ARRAY: False
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
    '''writePrime : expression printExpression writePrimePrime
                    | CST_STRING printString writePrimePrime'''


def p_printExpression(p):
    'printExpression :'
    typeStack.pop()
    quadruple = Quadruple(PRINT_EXP, None, None, operandStack.pop())
    quadruples.append(quadruple)


def p_printString(p):
    'printString :'
    quadruple = Quadruple(PRINT_STR, None, None, p[-1])
    quadruples.append(quadruple)


def p_writePrimePrime(p):
    '''writePrimePrime : COMA writePrime
                        | '''


def p_callVoidF(p):
    'callVoidF : ID addIdToStack callFunction SEMICOLON'


def p_callFunction(p):
    '''callFunction : LPAREN callFunction1 expressions RPAREN callFunction4'''


def p_callFunction1(p):
    'callFunction1 :'
    global checkFunction
    if checkFunction:
        checkFunction = False
        function_id = operandStack.top()
        # Esto es temporal hasta tener memoria, le tenemos que pasar la cantidad de vars.
        quad = Quadruple(ERA, functionDirectory[function_id][ADDRESS], None,
                         None)
        quadruples.append(quad)
        global paramCounter
        # este elda lo puso como 1 -- si tenemos problemas despues puede ser esto
        paramCounter = 0
    else:
        raise FunctionNotDeclared


def p_callFunction2(p):
    'callFunction2 :'
    argument = operandStack.pop()
    argumentType = typeStack.pop()
    function_id = operandStack.top()
    keys_list = list(paramTable[function_id])
    key = keys_list[paramCounter]
    if argumentType == paramTable[function_id][key][TYPE]:
        quad = Quadruple(PARAMETER, argument, None, paramCounter)
        quadruples.append(quad)
    else:
        raise TypeMismatchError


def p_callFunction3(p):
    'callFunction3 :'
    global paramCounter
    paramCounter = paramCounter + 1


def p_callFunction4(p):
    'callFunction4 :'
    global paramCounter
    function_id = operandStack.pop()
    idType = typeStack.pop()
    if paramCounter + 1 == len(paramTable[function_id]):
        result = getNextAddress(convert_type(idType, TEMPORAL_SCOPE))
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
    '''expressionsPrime : COMA callFunction3 expressions 
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
        quadEndfunc = Quadruple(END_FUNC, None, None, None)
        quadruples.append(quadruple)
        quadruples.append(quadEndfunc)


def p_read(p):
    'read : INPUT addOperator LPAREN readPrime RPAREN SEMICOLON'


def p_readPrime(p):
    'readPrime : ids2 readVar readPrimePrime'


def p_readVar(p):
    'readVar :'
    var = operandStack.pop()
    typeStack.pop()
    quadruple = Quadruple(operatorStack.pop(), None, None, var)
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
            result = getNextAddress(convert_type(resultType, TEMPORAL_SCOPE))
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
            result = getNextAddress(convert_type(opType, TEMPORAL_SCOPE))
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
            result = getNextAddress(convert_type(resultType, TEMPORAL_SCOPE))
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
            result = getNextAddress(convert_type(resultType, TEMPORAL_SCOPE))
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
            result = getNextAddress(convert_type(resultType, TEMPORAL_SCOPE))
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
        # Preparacion para hacer la comparacion aver si entra al for
        operandStack.push(leftSide)
        typeStack.push(leftType)
        operatorStack.push('==')
    else:
        # Error for loops must be ints
        raise TypeMismatchError


def p_addFor2(p):
    'addFor2 :'
    operator = operatorStack.pop()
    rightType = typeStack.pop()
    leftType = typeStack.pop()
    rightOperand = operandStack.pop()
    leftOperand = operandStack.pop()
    if rightType == INT and leftType == INT:
        result = getNextAddress(TEMPORAL_INT)
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
    operator = operatorStack.pop()
    leftSide = operandStack.pop()
    leftType = typeStack.pop()
    rightSide = '1'
    rightType = INT
    resultType = semanticCube[(leftType, rightType, operator)]
    if leftType == INT:
        result = getNextAddress(convert_type(resultType, TEMPORAL_SCOPE))
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
    address = getNextAddress(CONSTANT_FLOAT, value=p[-1], valType=FLOAT)
    operandStack.push(address)
    typeStack.push(FLOAT)


def p_addInt(p):
    'addInt :'
    address = getNextAddress(CONSTANT_INT, value=p[-1], valType=INT)
    operandStack.push(address)
    typeStack.push(INT)


def p_addChar(p):
    'addChar :'
    address = getNextAddress(CONSTANT_CHAR, value=p[-1], valType=CHAR)
    operandStack.push(address)
    typeStack.push(CHAR)


# Manejo de errores
def p_error(p):
    print("Syntax error at line %d, token=%s, value=%s col=%s" %
          (p.lineno, p.type, p.value, p.lexpos))
    exit()


def initAll():
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
    global forStack
    global function_id
    global function_type
    functionDirectory = {}
    variableTable = {}
    paramTable = {}
    varIds = Stack()
    currentType = ""
    checkFunction = False
    hasReturn = False
    paramCounter = 0
    operatorStack = Stack()
    operandStack = Stack()
    typeStack = Stack()
    jumpStack = Stack()
    forStack = Stack()
    quadruples = []
    function_id = ""
    function_type = ""
    resetAll()


# Constructor del parser
parser = yacc.yacc()

# pasar archivo de entrada
filename = sys.argv[-1]
f = open(filename, "r")

# parsear archivo
app = Flask(__name__)
CORS(app)


@app.route('/')
def root():
    return "Hello World"


@app.route('/compile', methods=["POST"])
def compile():
    content = request.get_json()
    quadDict = {}
    global countRuns
    countRuns = countRuns + 1
    if countRuns > 1:
        initAll()

    # Here we will pass to the vm
    # and return the result of the vm to the front
    try:
        parser.parse(content['codigo'])
        print('////', len(quadruples))
        vm.start(quadruples)
        for number, element in enumerate(quadruples):
            quadDict[number] = element.generateLista()
        return quadDict
    except Exception as e:
        errors = {1: str(e)}
        return errors


if __name__ == "__main__":
    app.run(host='0.0.0.0')
