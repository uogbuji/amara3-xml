# amara3.uxml.uxpath.lexrules
'''
Heavy debt to: https://github.com/emory-libraries/eulxml/blob/master/eulxml/xpath/lexrules.py

'''

import re
from ply.lex import TOKEN


OPERATOR_NAMES = {
    'or': 'OR_OP',
    'and': 'AND_OP',
    'div': 'DIV_OP',
    'mod': 'MOD_OP',
}

tokens = [
        'PATH_SEP',
        'ABBREV_PATH_SEP',
        'ABBREV_STEP_SELF',
        'ABBREV_STEP_PARENT',
        'AXIS_SEP',
        'ABBREV_AXIS_AT',
        'OPEN_PAREN',
        'CLOSE_PAREN',
        'OPEN_BRACKET',
        'CLOSE_BRACKET',
        'UNION_OP',
        'EQUAL_OP',
        'REL_OP',
        'PLUS_OP',
        'MINUS_OP',
        'MULT_OP',
        'STAR_OP',
        'COMMA',
        'LITERAL',
        'FLOAT',
        'INTEGER',
        'NODETEXTTEST',
        'NAME',
        'DOLLAR',
    ] + list(OPERATOR_NAMES.values())

t_PATH_SEP = r'/'
t_ABBREV_PATH_SEP = r'//'
t_ABBREV_STEP_SELF = r'\.'
t_ABBREV_STEP_PARENT = r'\.\.'
t_AXIS_SEP = r'::'
t_ABBREV_AXIS_AT = r'@'
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACKET = r'\['
t_CLOSE_BRACKET = r'\]'
t_UNION_OP = r'\|'
t_EQUAL_OP = r'!?='
t_REL_OP = r'[<>]=?'
t_PLUS_OP = r'\+'
t_MINUS_OP = r'-'
t_COMMA = r','
t_DOLLAR = r'\$'
t_STAR_OP = r'\*'


t_ignore = ' \t\r\n'

NameStartChar = r'(' + r'[A-Z]|_|[a-z]|\xc0-\xd6]|[\xd8-\xf6]|[\xf8-\u02ff]|' + \
    r'[\u0370-\u037d]|[\u037f-\u1fff]|[\u200c-\u200d]|[\u2070-\u218f]|' + \
    r'[\u2c00-\u2fef]|[\u3001-\uD7FF]|[\uF900-\uFDCF]|[\uFDF0-\uFFFD]' + \
    r'|[\U00010000-\U000EFFFF]' + r')'
# additional characters allowed in NCNames after the first character
NameChar_extras = r'[-.0-9\xb7\u0300-\u036f\u203f-\u2040]'

NAME_REGEX = r'(' + NameStartChar + r')(' + \
                    NameStartChar + r'|' + NameChar_extras + r')*'

NODE_TYPES = set(['text', 'node'])

@TOKEN(NAME_REGEX)
def t_NAME(t):
    # Check for operators
    t.type = OPERATOR_NAMES.get(t.value, 'NAME')
    return t

def t_LITERAL(t):
    r""""[^"]*"|'[^']*'"""
    t.value = t.value[1:-1]
    return t

def t_FLOAT(t):
    r'\d+\.\d*|\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NODETEXTTEST(t):
    r'text\(\)|node\(\)'
    return t

def t_error(t):
    raise TypeError("Unknown text '{}'".format(t.value))

