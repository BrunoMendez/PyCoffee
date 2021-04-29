# Bruno Mendez A01194018
# Esteban Torres A01193925

import ply.yacc as yacc
import sys
import lexer
from datastructures import *

tokens = lexer.tokens

currentScope = "global"
functionDirectory = {}
variableTable = {}
varIds = Queue()
currentType = ""

operatorStack = Stack()
operandStack = Stack()
typeStack = Stack()
jumpStack = Stack()
avail = Queue()

# Toma precedencia ( sobre ID para no reducir ID cuando llamamos una funcion.
precedence = (
    ('nonassoc', 'ID'),
    ('nonassoc', 'LPAREN'),
)


# Definicion de reglas de la gramatica
def p_program(p):
    'program : PROGRAM ID createGlobalTables SEMICOLON vars functions MAIN LPAREN RPAREN block'
    print(variableTable)
    print(functionDirectory)


def p_createGlobalTables(p):
    'createGlobalTables : '
    currentScope = "global"
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
    '''ids2 : ID 
            | ID arrPos'''


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
    'assignment : ids2 EQUAL expression SEMICOLON'


def p_write(p):
    '''write : PRINT LPAREN writePrime RPAREN SEMICOLON'''


def p_writePrime(p):
    '''writePrime : expression writePrimePrime
                    | CST_STRING writePrimePrime'''


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
    'readPrime : ids2 readPrimePrime'


def p_readPrimePrime(p):
    '''readPrimePrime : COMA readPrime
                    | '''


def p_repetition(p):
    '''repetition : conditional
                    | nonConditional'''


def p_decision(p):
    'decision : IF LPAREN expression RPAREN block decisionPrime'


def p_decisionPrime(p):
    '''decisionPrime : ELSE block 
                    | '''


def p_conditional(p):
    'conditional : WHILE LPAREN expression RPAREN block'


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
    '''callableCst : ID
                |  ID callFunction
                | ID arrPos'''
    if (p[1] != None):
        print(" cst: ", p[1])


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
            # result <- avail.next()
            if operator == 'and':
                result = (leftOperand != '0' and rightOperand != '0')
            else:
                result = (leftOperand != '0' or rightOperand != '0')
            quadruple = Quadruple(operator, leftOperand, rightOperand, result)
            operandStack.push(quadruple.result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
            print("andor ", quadruple.result)
        else:
            raise SyntaxError


def p_addNot(p):
    'addNot :'
    if (operatorStack.top() == 'not'):
        operator = operatorStack.pop()
        opType = typeStack.pop()
        operand = operandStack.pop()
        print(operand)
        if (opType == 'int'):
            # result <- avail.next()
            result = operand == '0'
            quadruple = Quadruple(operator, operand, None, result)
            operandStack.push(quadruple.result)
            typeStack.push('int')
            # if any operand were a temporal space return it to avail
            print(quadruple.result)
        else:
            raise SyntaxError


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
            # result <- avail.next()
            quadruple = Quadruple(operator, leftOperand, rightOperand, "tx")
            operandStack.push(quadruple.result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
            print(quadruple.result)
        else:
            raise SyntaxError


def p_addTerm(p):
    'addTerm :'
    if (operatorStack.top() in ['+', '-']):
        operator = operatorStack.pop()
        rightType = typeStack.pop()
        leftType = typeStack.pop()
        rightOperand = getConvertedOperand(operandStack.pop(), rightType)
        leftOperand = getConvertedOperand(operandStack.pop(), leftType)
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != 'error':
            # result <- avail.next()
            if (operator == '+'):
                result = leftOperand + rightOperand
            elif (operator == '-'):
                result = leftOperand - rightOperand
            else:
                raise SyntaxError
                # error('type mismatch') ---- we need to program the errors
            quadruple = Quadruple(operator, leftOperand, rightOperand, result)
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail

            print(quadruple.result)
        else:
            raise SyntaxError


def p_addFactor(p):
    'addFactor :'
    if (operatorStack.top() in ['*', '/']):
        print(operatorStack)
        print(operandStack)
        print(typeStack)
        operator = operatorStack.pop()
        print(operator)
        rightType = typeStack.pop()
        print(rightType)
        rightOperand = getConvertedOperand(operandStack.pop(), rightType)
        leftType = typeStack.pop()
        leftOperand = getConvertedOperand(operandStack.pop(), leftType)
        print(leftType, rightType, operator)
        resultType = semanticCube[(leftType, rightType, operator)]
        if resultType != 'error':
            # result <- avail.next()
            if (operator == '*'):
                result = leftOperand * rightOperand
            elif (operator == '/'):
                result = leftOperand / rightOperand
            else:
                raise SyntaxError
                # error('type mismatch') ---- we need to program the errors
            quadruple = Quadruple(operator, leftOperand, rightOperand, result)
            operandStack.push(result)
            typeStack.push(resultType)
            # if any operand were a temporal space return it to avail
            print(quadruple.result)
        else:
            raise SyntaxError
def p_decision(p):
    'decision :'
    exp_type = typeStack.pop()
    # Falta logica del GoToF
    # Falta logica del GotoV
    # Falta logica del Goto
    # si el if se cumple entonces evalua lo de adentro
    # si no salta al else
    GotoF = ''
    if (exp_type != int):
        raise SyntaxError
    else:
        result = operandStack.pop()
        quadruple = Quadruple(GotoF, result, '', '')
        # cont son los tokens???
        end = jumpStack.push(p-1)
    end = jumpStack.pop()
    # que hace el FILL???
    #FILL(end, p)
    # manejamos misma logica para el else ?
    # tenemos funcion decisionPrime que incluye al else

def p_conditional(p):
    'conditional : '
    # es jumpStack(p) ???
    jumpStack.push(p)
    exp_type = typeStack.pop()
    # Falta definir GoToF
    GotoF = ''
    if(exp_type != int):
        raise SyntaxError
        # Logica de manejo de errors
        #error('Type Mismatch')
    else:
        result = operandStack.pop()
        quadruple = Quadruple(GoToF, result, '', '')
        jumpStack.push(p-1)
    end = jumpStack.pop()
    #return=jumpStack.pop() ??? return is a reserved word 
    # are we meant to return that ?
    ret=jumpStack.pop()
    quadruple = Quadruple(GoTo, ret, '', '')
    #FILL(end,p)

def getConvertedOperand(operand, opType):
    print(operand)
    if (opType == 'int'):
        return int(operand)
    elif (opType == 'float'):
        return float(operand)
    return operand


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
    print("Syntax error in input!")


# Constructor del parser
parser = yacc.yacc()

# pasar archivo de entrada
filename = sys.argv[-1]
f = open(filename, "r")

# parsear archivo
result = parser.parse(f.read())

# print(result)
