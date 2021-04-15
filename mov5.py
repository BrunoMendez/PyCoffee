# Bruno Mendez A01194018
# Esteban Torres A01193925

import ply.lex as lex
import ply.yacc as yacc
import sys

# Lista de nombres de tokens.
tokens = [
    'ID',
    'SEMICOLON',
    'COLON',
    'COMA',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'EQUAL',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'CST_STRING',
    'CST_CHAR',
    'CST_INT',
    'CST_FLOAT',
    'LT',
    'GT',
    'NE'
]

# Lista de palabras reservadas.
reserved = {
    'program'   : 'PROGRAM',
    'var'       : 'VAR',
    'function'  : 'FUNCTION',
    'int'       : 'INT',
    'float'     : 'FLOAT',
    'char'      : 'CHAR',
    'void'      : 'VOID',
    'print'     : 'PRINT',
    'input'     : 'INPUT',
    'if'        : 'IF',
    'else'      : 'ELSE',
    'main'      : 'MAIN',
    'return'    : 'RETURN',
    'while'     : 'WHILE',
    'for'       : 'FOR',
}
tokens += reserved.values()

# Regexpr para tokens simples
t_SEMICOLON     = r';'
t_COLON         = r':'
t_COMA          = r','
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_LBRACKET      = r'\['
t_RBRACKET      = r'\]'
t_EQUAL         = r'='
t_PLUS          = r'\+'
t_MINUS         = r'-'
t_MULTIPLY      = r'\*'
t_DIVIDE        = r'/'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_CST_STRING    = r'("(\\"|[^"])*")'
t_CST_CHAR      = r'[a-zA-Z]'
t_CST_INT       = r'[0-9]+'
t_CST_FLOAT     = r'[0-9]+\.[0-9]+'
t_LT            = r'<'
t_GT            = r'>'



# Regexpr para tokens que requieren más codigo
def t_ID(token):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    if token.value in reserved:
        token.type = reserved[token.value]
    return token

# Regla para tomar en cuenta cambios de linea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Caracteres a ignorar
t_ignore  = ' \t'
t_ignore_COMMENT = r'%%.*'


# Manejo de errores
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Constructor del lexer
lexer = lex.lex()

# Definicion de reglas de la gramatica
def p_program(p):
    'program : PROGRAM ID SEMICOLON createGlobalTables vars functions MAIN LPAREN RPAREN block'

def p_createGlobalTables(p):
    'createGlobalTables : '
    
    #global currentScope = "global"
    
    #global functionDirectory = {currentScope: {"type": "void"} }
    #global variableTables = {}

def p_vars(p):
    '''vars : VAR varsPrime 
            | empty'''

def p_varsPrime(p):
    '''varsPrime : listIds COLON type SEMICOLON addVarsToTable varsPrime 
                | empty'''

def p_addVarsToTable(p):
    'addVarsToTable : '

def p_functions(p):
    '''functions : function functions
                | empty'''
    
def p_listIds(p):
    '''listIds : ids listIdsPrime'''

def p_listIdsPrime(p):
    '''listIdsPrime : COMA ids listIdsPrime 
                    | empty'''

def p_ids(p):
    '''ids : ID 
            | ID LBRACKET CST_INT RBRACKET 
            | ID LBRACKET CST_INT RBRACKET LBRACKET CST_INT RBRACKET'''

def p_ids2(p):
    '''ids2 : ID 
            | ID LBRACKET exp RBRACKET 
            | ID LBRACKET exp RBRACKET LBRACKET exp RBRACKET'''

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''

def p_returnType(p):
    '''returnType : type
                    | VOID'''

def p_function(p):
    'function : returnType FUNCTION ID LPAREN params RPAREN vars block'

def p_params(p):
    'params : ids COLON type paramsPrime'

def p_paramsPrime(p):
    '''paramsPrime : params COMA 
                | empty'''

def p_block(p):
    '''block : LBRACE statutes RBRACE'''

def p_statutes(p):
    '''statutes : statute 
                | statutesPrime'''

def p_statutesPrime(p):
    '''statutesPrime : statutes
                    | empty'''

def p_statute(p):
    '''statute : assignment
                | conditional
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
                        | empty'''

def p_callVoidF(p):
    '''callVoidF : ID LPAREN callVoidFPrime RPAREN SEMICOLON'''

def p_callVoidFPrime(p):
    '''callVoidFPrime : varCst
                    | empty'''

def p_return(p):
    'return : RETURN LPAREN exp RPAREN SEMICOLON'

def p_read(p):
    'read : INPUT LPAREN readPrime RPAREN SEMICOLON'

def p_readPrime(p):
    'readPrime : ids2 readPrimePrime'

def p_readPrimePrime(p):
    '''readPrimePrime : COMA readPrime
                    | empty'''

def p_repetition(p):
    '''repetition : conditional
                    | nonConditional'''

def p_decision(p):
    'decision : IF LPAREN exp RPAREN block decisionPrime'

def p_decisionPrime(p):
    '''decisionPrime : ELSE block 
                    | empty'''

def p_conditional(p):
    'conditional : WHILE LPAREN expression RPAREN block'

def p_nonConditional(p):
    'nonConditional : FOR LPAREN ids2 EQUAL exp COLON exp RPAREN block'

def p_expression(p):
    '''expression : exp GT exp
                | exp LT exp
                | exp NE exp
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
            | PLUS varCst
            | MINUS varCst
            | varCst'''

def p_varCst(p):
    '''varCst : ID
            | CST_FLOAT 
            | CST_INT
            | CST_CHAR
            | CST_STRING'''

def p_empty(p):
    'empty :'
    pass

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