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

GLOBAL_SCOPE = "global"
currentScope = GLOBAL_SCOPE
functionDirectory = {}
variableTable = {}
varIds = Queue()
currentType = ""

operatorStack = Stack()
operandStack = Stack()
typeStack = Stack()
jumpStack = Stack()
quadruples = []
temps = 0
# changes on quadruples better to have it as a list for simplicity

# definition of avail


def next_avail():
    global temps
    temps = temps + 1
    return "t" + str(temps)


# Toma precedencia ( sobre ID para no reducir ID cuando llamamos una funcion.
precedence = (
    ('right', 'ID', 'LPAREN'),
    ('nonassoc', 'LPAREN'),
)


# Definicion de reglas de la gramatica
def p_program(p):
    'program : PROGRAM ID createGlobalTables SEMICOLON vars functions MAIN LPAREN RPAREN block'
    print(variableTable)
    print(functionDirectory)
    for quadruple in quadruples:
        print(quadruple)


def p_createGlobalTables(p):
    'createGlobalTables : '
    currentScope = GLOBAL_SCOPE
    functionDirectory[currentScope] = "void"
    variableTable[currentScope] = {}


def p_vars(p):
    '''vars : VAR varsPrime 
            | '''


def p_varsPrime(p):
    '''varsPrime : listIds COLON type addVars SEMICOLON varsPrime 
                | '''


def p_addVars(p):
    'addVars :'
    while not varIds.empty():
        variableTable[currentScope][varIds.dequeue()] = {
            "type": currentType,
            "value": []
        }


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


def p_ids2(p):
    '''ids2 : ID addIdToStack
            | ID arrPos'''


def p_addIdToStack(p):
    'addIdToStack :'
    # manejar arrays
    varId = p[-1]
    if (varId in variableTable[currentScope]):
        typeStack.push(variableTable[currentScope][varId]["type"])
        operandStack.push(varId)
    elif (varId in variableTable[GLOBAL_SCOPE]):
        typeStack.push(variableTable[GLOBAL_SCOPE][varId]["type"])
        operandStack.push(varId)
    else:
        raise TypeMismatchError


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
    'function : returnType FUNCTION ID addFunction LPAREN params RPAREN vars block'
    global currentScope
    del variableTable[currentScope]
    currentScope = "global"


def p_addFunction(p):
    'addFunction :'
    global currentScope
    currentScope = p[-1]
    functionDirectory[currentScope] = currentType
    variableTable[currentScope] = {}


def p_params(p):
    'params : ids COLON type addVars paramsPrime'


def p_paramsPrime(p):
    '''paramsPrime : params COMA 
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
    'assignment : ids2 EQUAL addOperator expression SEMICOLON'
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


def p_write(p):
    '''write : PRINT addOperator LPAREN writePrime RPAREN SEMICOLON'''


def p_writePrime(p):
    '''writePrime : expression printExpression writePrimePrime
                    | CST_STRING printString writePrimePrime'''


def p_printExpression(p):
    'printExpression :'
    quadruple = Quadruple("print", None, None, operandStack.pop())
    quadruples.append(quadruple)


def p_printString(p):
    'printString :'
    quadruple = Quadruple("print", None, None, p[-1])
    quadruples.append(quadruple)


def p_writePrimePrime(p):
    '''writePrimePrime : COMA writePrime
                        | '''


def p_callVoidF(p):
    'callVoidF : ID callFunction SEMICOLON'


def p_callFunction(p):
    '''callFunction : LPAREN expressions RPAREN'''


def p_expressions(p):
    '''expressions : expression expressionsPrime 
                |'''


def p_expressionsPrime(p):
    '''expressionsPrime : COMA expression expressionsPrime 
                        |'''


def p_return(p):
    'return : RETURN LPAREN expression RPAREN SEMICOLON'


def p_read(p):
    'read : INPUT LPAREN readPrime RPAREN SEMICOLON'


def p_readPrime(p):
    'readPrime : ids2 readVar readPrimePrime'


def p_readVar(p):
    'readVar :'
    var = operandStack.pop()
    typeStack.pop()
    quadruple = Quadruple("read", None, None, var)
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
    'nonConditional : FOR LPAREN ids2 EQUAL exp COLON exp RPAREN block'


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
    '''callableCst : ID addIdToStack
                |  ID callFunction
                | ID arrPos'''


def p_popOperator(p):
    'popOperator :'
    operatorStack.pop()


def p_addOperator(p):
    'addOperator :'
    operatorStack.push(p[-1])


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
        quadruple = Quadruple("GOTOF", result, None, None)
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
    quadruple = Quadruple("GOTO", None, None, None)
    quadruples.append(quadruple)
    jumpStack.push(len(quadruples) - 1)
    quadruples[false] = Quadruple("GOTOF", quadruples[false].leftOperand, None,
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
        quadruple = Quadruple("GOTOF", result, None, None)
        quadruples.append(quadruple)
        jumpStack.push(len(quadruples) - 1)


def p_addWhile3(p):
    'addWhile3 : '
    end = jumpStack.pop()
    ret = jumpStack.pop()
    quadruple = Quadruple("GOTO", None, None, ret)
    quadruples.append(quadruple)
    quadruples[end] = Quadruple(quadruples[end].operator,
                                quadruples[end].leftOperand, None,
                                len(quadruples))


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