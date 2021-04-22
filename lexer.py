import ply.lex as lex

# Lista de nombres de tokens.
tokens = [
    'ID', 'SEMICOLON', 'COLON', 'COMA', 'LBRACE', 'RBRACE', 'LBRACKET',
    'RBRACKET', 'EQUAL', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'LPAREN',
    'RPAREN', 'CST_STRING', 'CST_CHAR', 'CST_INT', 'CST_FLOAT', 'LT', 'GT',
    'NE', 'EQEQ', 'LTEQ', 'GTEQ'
]

# Lista de palabras reservadas.
reserved = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'function': 'FUNCTION',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'void': 'VOID',
    'print': 'PRINT',
    'input': 'INPUT',
    'if': 'IF',
    'else': 'ELSE',
    'main': 'MAIN',
    'return': 'RETURN',
    'while': 'WHILE',
    'for': 'FOR',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT'
}
tokens += reserved.values()

# Regexpr para tokens simples
t_SEMICOLON = r';'
t_COLON = r':'
t_COMA = r','
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUAL = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_CST_STRING = r'("(\\"|[^"])*")'
t_CST_CHAR = r'\'[a-zA-Z]\''
t_CST_INT = r'[0-9]+'
t_CST_FLOAT = r'[0-9]+\.[0-9]+'
t_LT = r'<'
t_GT = r'>'
t_NE = r'<>'
t_EQEQ = r'=='
t_LTEQ = r'<='
t_GTEQ = r'>='


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
t_ignore = ' \t'
t_ignore_COMMENT = r'%%.*'


# Manejo de errores
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Constructor del lexer
lexer = lex.lex()