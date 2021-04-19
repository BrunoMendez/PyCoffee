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
        variableTable[currentScope][varIds.dequeue()] = currentType

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
    if(p[1] == 'void'):
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
    '''block : LBRACE statutes RBRACE'''

def p_statutes(p):
    '''statutes : statute statutes 
                | '''

def p_statute(p):
    '''statute : assignment
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
    'callVoidF : callFunction SEMICOLON'

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
    '''expression : miniExpression AND miniExpression
                    | miniExpression OR miniExpression
                    | miniExpression'''

def p_miniExpression(p):
    '''miniExpression : exp GT exp
                | exp LT exp
                | exp NE exp
                | exp EQEQ exp
                | exp LTEQ exp
                | exp GTEQ exp
                | exp'''

def p_exp(p):
    '''exp : term
            | term PLUS exp
            | term MINUS exp'''

def p_term(p):
    '''term : factor 
            | factor MULTIPLY term 
            | factor DIVIDE term'''

def p_factor(p):
    '''factor : LPAREN expression RPAREN
                | varCst'''

def p_varCst(p):
    '''varCst : ID
            | callFunction
            | ID arrPos
            | CST_FLOAT 
            | CST_INT
            | CST_CHAR'''

def p_callFunction(p):
    '''callFunction : ID LPAREN expressions RPAREN'''

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