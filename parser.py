# Bruno Mendez A01194018
# Esteban Torres A01193925
# bug report ----> si no especificas la variable arriba del programa se queda esperando y no arroja ningun resultado
# hacer algo para que si se pone una variable que no existe en la tabla regresar un error(variable not declared!)
# no estamos pasando el tipo de la variable al typeStack
import ply.yacc as yacc
import sys
import lexer
from errors import *
from datastructures import *

tokens = lexer.tokens

FUNCTION_TYPE = "type"
FUNCTION_PARAM_COUNT = "paramCount"
FUNCTION_VAR_COUNT = "varCount"
FUNCTION_TEMP_COUNT = "tempCount"
FUNCTION_QUAD_INDEX = "quadIndex"
GLOBAL_SCOPE = "global"
GOTO = "GOTO"
END_FUNC = "ENDFunc"
ERA = "ERA"
GOTOF = "GOTOF"
GOSUB = "GOSUB"
PARAMETER = "PARAMETER"
RETURN = "RETURN"
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
forStack = Stack()
quadruples = []
temps = 0
function_id = ""
function_type = ""

# changes on quadruples better to have it as a list for simplicity

# definition of avail


def next_avail():
    global temps
    temps = temps + 1
    return "t" + str(temps)


# Toma precedencia ( sobre ID para no reducir ID cuando llamamos una funcion.
precedence = (
    ('right', 'ID'),
    ('nonassoc', 'LPAREN'),
)


# Definicion de reglas de la gramatica
def p_program(p):
    'program : PROGRAM ID createGlobalTables SEMICOLON vars functions MAIN LPAREN RPAREN mainStart block'
    functionDirectory[GLOBAL_SCOPE][FUNCTION_TEMP_COUNT] = temps
    print(variableTable)
    print(functionDirectory)
    for quadruple in quadruples:
        print(quadruple)
    print(paramTable)
    print(typeStack)
    print(operandStack)


def p_mainStart(p):
    'mainStart :'
    quadruples[0].result = len(quadruples)
    functionDirectory[GLOBAL_SCOPE][FUNCTION_QUAD_INDEX] = len(quadruples)
    functionDirectory[GLOBAL_SCOPE][FUNCTION_VAR_COUNT] = len(
        variableTable[GLOBAL_SCOPE])


def p_createGlobalTables(p):
    'createGlobalTables : '
    currentScope = GLOBAL_SCOPE
    functionDirectory[currentScope] = {
        FUNCTION_TYPE: "void",
        FUNCTION_PARAM_COUNT: 0,
        FUNCTION_VAR_COUNT: 0,
        FUNCTION_QUAD_INDEX: 0,
        FUNCTION_TEMP_COUNT: 0
    }
    variableTable[currentScope] = {}
    quad = Quadruple(GOTO, "main", None, None)
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
        var = varIds.dequeue()
        if (var in variableTable[currentScope]):
            # Variable already defined error
            #print("var already in table")
            raise VarAlreadyInTable
            exit()
        else:
            variableTable[currentScope][var] = {"type": currentType}


def p_addFunction2(p):
    'addFunction2 :'
    while not varIds.empty():
        var = varIds.dequeue()
        if (var in variableTable[currentScope]):
            # Variable already defined error
            #print("var already in table")
            raise VarAlreadyInTable
            exit()
        else:
            variableTable[currentScope][var] = {"type": currentType}
            paramTable[currentScope][var] = {"type": currentType}


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
            | ID addId LBRACKET CST_INT RBRACKET 
            | ID addId LBRACKET CST_INT RBRACKET LBRACKET CST_INT RBRACKET'''


def p_addId(p):
    'addId :'
    varIds.enqueue(p[-1])


def p_checkIfNotFunction(p):
    'checkIfNotFunction :'
    if checkFunction:
        raise VarNotDefined


def p_ids2(p):
    '''ids2 : ID addIdToStack checkIfNotFunction
            | ID arrPos'''


def p_addIdToStack(p):
    'addIdToStack :'
    # manejar arrays
    varId = p[-1]
    if varId in functionDirectory:
        global checkFunction
        checkFunction = True
        typeStack.push(functionDirectory[varId]["type"])
        operandStack.push(varId)
    elif (varId in variableTable[currentScope]):
        typeStack.push(variableTable[currentScope][varId]["type"])
        operandStack.push(varId)
    elif (varId in variableTable[GLOBAL_SCOPE]):
        typeStack.push(variableTable[GLOBAL_SCOPE][varId]["type"])
        operandStack.push(varId)
    else:
        raise VarNotDefined


def p_arrPos(p):
    '''arrPos : LBRACKET exp RBRACKET 
                | LBRACKET exp RBRACKET LBRACKET exp RBRACKET'''


def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''
    global currentType
    currentType = p[1]


def p_returnType(p):
    '''returnType : type
                    | VOID'''
    if (p[1] == 'void'):
        global currentType
        currentType = p[1]


def p_function(p):
    'function : returnType FUNCTION ID addFunction1 LPAREN params RPAREN addFunction3 vars addFunction4 block'
    global currentScope
    global temps
    functionDirectory[currentScope][FUNCTION_TEMP_COUNT] = temps
    del variableTable[currentScope]
    currentScope = "global"
    temps = 0
    if (function_type != 'void' and (not hasReturn)):
        raise NonVoidFuncReturnMissing
    elif not hasReturn and function_type == 'void':
        quadruples.append(Quadruple(END_FUNC, None, None, None))


def p_addFunction4(p):
    'addFunction4 :'
    functionDirectory[currentScope][FUNCTION_VAR_COUNT] = len(
        variableTable[currentScope])
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
    functionDirectory[currentScope][FUNCTION_TYPE] = currentType
    variableTable[currentScope] = {}
    function_id = currentScope
    function_type = currentType
    if (function_type != 'void'):
        if (function_id in variableTable[GLOBAL_SCOPE]):
            raise VarAlreadyInTable
        variableTable[GLOBAL_SCOPE][function_id] = {'type': function_type}


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
    '''write : PRINT addOperator LPAREN writePrime RPAREN SEMICOLON'''


def p_writePrime(p):
    '''writePrime : expression printExpression writePrimePrime
                    | CST_STRING printString writePrimePrime'''


def p_printExpression(p):
    'printExpression :'
    typeStack.pop()
    quadruple = Quadruple(operatorStack.pop(), None, None, operandStack.pop())
    quadruples.append(quadruple)


def p_printString(p):
    'printString :'
    typeStack.pop()
    quadruple = Quadruple(operatorStack.pop(), None, None, p[-1])
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
        quad = Quadruple(ERA, function_id, None, None)
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
    if argumentType == paramTable[function_id][key]['type']:
        quad = Quadruple(PARAMETER, argument, paramCounter, None)
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
    typeStack.pop()
    if paramCounter + 1 == len(paramTable[function_id]):
        result = next_avail()
        quad = Quadruple(GOSUB, function_id, None,
                         functionDirectory[function_id][FUNCTION_QUAD_INDEX])
        quadruples.append(quad)
        if functionDirectory[function_id][FUNCTION_TYPE] != "void":
            assignQuad = Quadruple('=', function_id, None, result)
            quadruples.append(assignQuad)
            operandStack.push(result)
            typeStack.push(functionDirectory[function_id][FUNCTION_TYPE])
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
    if (res_type != variableTable[GLOBAL_SCOPE][function_id]['type']):
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
                | ID arrPos'''


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
    if (opType != "error"):
        # esto estaba asi -> Quadruple(operator, None, res, leftSide)
        quadruple = Quadruple(operator, res, None, leftSide)
        quadruples.append(quadruple)
    else:
        # Create error message
        raise TypeMismatchError


def p_addAndOr(p):
    'addAndOr :'
    if (operatorStack.top() in ['and', 'or']):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = operandStack.pop()
        leftOperand = operandStack.pop()
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != 'error':
            result = next_avail()
            quadruples.append(
                Quadruple(operator, leftOperand, rightOperand, result))
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
        else:
            raise TypeMismatchError()


def p_addNot(p):
    'addNot :'
    if (operatorStack.top() == 'not'):
        operator = operatorStack.pop()
        opType = typeStack.pop()
        operand = operandStack.pop()
        if (opType == 'int'):
            result = next_avail()
            quadruples.append(Quadruple(operator, operand, None, result))
            operandStack.push(result)
            typeStack.push('int')
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
        if resultType != 'error':
            result = next_avail()
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
        if resultType != 'error':
            result = next_avail()
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
        if resultType != 'error':
            result = next_avail()
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
    if exp_type != 'int':
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
    if (exp_type != "int"):
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
    if (resType == "int" and leftType == "int"):
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
    if rightType == 'int' and leftType == 'int':
        result = next_avail()
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
    rightType = 'int'
    resultType = semanticCube[(leftType, rightType, operator)]
    if leftType == 'int':
        result = next_avail()
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
    operandStack.push(p[-1])
    typeStack.push('float')


def p_addInt(p):
    'addInt :'
    operandStack.push(p[-1])
    typeStack.push('int')


def p_addChar(p):
    'addChar :'
    operandStack.push(p[-1])
    typeStack.push('char')


# Manejo de errores
def p_error(p):
    print("Syntax error at line %d, token=%s, value=%s col=%s" %
          (p.lineno, p.type, p.value, p.lexpos))
    exit()


# Constructor del parser
parser = yacc.yacc()

# pasar archivo de entrada
filename = sys.argv[-1]
f = open(filename, "r")

# parsear archivo
result = parser.parse(f.read())

# print(result)