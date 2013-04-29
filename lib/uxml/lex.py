# -----------------------------------------------------------------------------
# amara3.uxml.lex
#
# MicroXML scanner
#  This is not a full parser, e.g. it doesn't ignore comments, it preserves attribute order, which quotes are used, etc.
#  It is rather meant as a foundation for proper parsers
# -----------------------------------------------------------------------------

import sys

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc

tokens = (
    'NAME','STARTTAG','ENDTAG','GT', 'EQ', 'BOM',
    'ATTVAL1','ATTVAL2','NAMEDCHARREF', 'COMMENT', 'CHARDATA',
    'SGL_QUOTE','DBL_QUOTE',
    'AMP_ENT', 'LT_ENT', 'GT_ENT', 'APOS_ENT', 'QUOT_ENT', 'NUM_ENT',
    )

states = (
   ('tag','exclusive'),
   ('data','exclusive'),
   ('attrsgl','exclusive'),
   ('attrdbl','exclusive'),
)

BOM = '\uFEFF'

CHARACTER = '[\u0009\u000a\u0020-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

#MicroXML production [7] Basically CHARACTER - [\u0026\u003C\u003E]
DATACHAR = '[\u0009\u000a\u0020-\u0025\u0027-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

NAMESTARTCHAR = '[A-Za-z_\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D' \
            '\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF' \
            '\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'

NAMECHAR =  '[0-9A-Za-z_\u00B7-\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u037D' \
            '\u037F-\u1FFF\u200C-\u200D\u203F-\u2040\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF' \
            '\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'

#For single quoted attrs
ATTRIBVALCHAR_SGL = '[\u0020-\u0025\u0028-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

#For double quoted attrs
ATTRIBVALCHAR_DBL = '[\u0020-\u0021\\\u0023-\u0025\u0027-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

# Tokens

WS = '[\u0009\u000A\u0020]'

@TOKEN(BOM)
def t_BOM(t):
    t.lexer.begin('data')
    return t

#t_NAME = '{0}{1}*'.format(NAMESTARTCHAR, NAMECHAR)
NAME_PAT = '{0}{1}*'.format(NAMESTARTCHAR, NAMECHAR)
@TOKEN(NAME_PAT)
def t_tag_NAME(t):
    return t
#t_NAME.__doc__ = '{0}{1}*'.format(NAMESTARTCHAR, NAMECHAR)

@TOKEN('<{0}*{1}{0}*'.format(WS, NAME_PAT, WS))
def t_data_STARTTAG(t):
    t.lexer.begin('tag')
    t.value = t.value[1:].strip()
    return t

@TOKEN('</{0}*{1}{0}*>'.format(WS, NAME_PAT, WS))
def t_data_ENDTAG(t):
    t.lexer.begin('data')
    t.value = t.value[2:-1].strip()
    return t

@TOKEN('>')
def t_tag_GT(t):
    t.lexer.begin('data')
    return t

@TOKEN('\'')
def t_tag_SGL_QUOTE(t):
    t.lexer.begin('attrsgl')
    return t

@TOKEN('"')
def t_tag_DBL_QUOTE(t):
    t.lexer.begin('attrdbl')
    return t

@TOKEN('\'')
def t_attrsgl_SGL_QUOTE(t):
    t.lexer.begin('tag')
    return t

@TOKEN('"')
def t_attrdbl_DBL_QUOTE(t):
    t.lexer.begin('tag')
    return t

@TOKEN('{0}+'.format(ATTRIBVALCHAR_SGL))
def t_attrsgl_CHARDATA(t):
    return t

@TOKEN('{0}+'.format(ATTRIBVALCHAR_DBL))
def t_attrdbl_CHARDATA(t):
    return t

@TOKEN('&\#x[0-9A-Fa-f]+;')
def t_attrdbl_NUM_ENT(t):
    t.value = t.value[3:-1]
    return t

@TOKEN('<!--{0}*-->'.format(DATACHAR))
def t_data_COMMENT(t):
    t.value = t.value[4:-3]
    return t

t_tag_EQ = '='

t_data_GT = '>'
t_data_CHARDATA = '{0}+'.format(DATACHAR)

t_data_AMP_ENT = t_attrsgl_AMP_ENT = t_attrdbl_AMP_ENT = '&amp;'
t_data_LT_ENT = t_attrsgl_LT_ENT = t_attrdbl_LT_ENT = '&lt;'
t_data_GT_ENT = t_attrsgl_GT_ENT = t_attrdbl_GT_ENT = '&gt;'
t_data_QUOT_ENT = t_attrsgl_QUOT_ENT = t_attrdbl_QUOT_ENT = '&quot;'
t_data_APOS_ENT = t_attrsgl_APOS_ENT = t_attrdbl_APOS_ENT = '&apos;'
t_data_NUM_ENT = t_attrsgl_NUM_ENT = t_attrdbl_NUM_ENT

#t_COMMENT = '<!--{0}*-->'.format(CHARACTER)

#import re
#print(t_NAMESEG)
#print(re.compile(CHARACTER))

# Ignored characters
#t_ignore = " \t\n"

def t_error(t):
    print("Illegal character '{0}'".format(repr(t.value[0])), file=sys.stderr)
    t.lexer.skip(1)

t_data_error = t_tag_error = t_attrsgl_error = t_attrdbl_error = t_error

# FIXME: Terribly non-reentrant with use of global here.  Right now it's because the lexer is so slow to build.  Figure out how to mitigate...
# Build the lexer
lexer = lex.lex() #debug=True
lexer.begin('data')

def run(s):
    s = s.replace(u'\r\n', u'\n')
    s = s.replace(u'\r', u'\n')
    lexer.input(s)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break      # No more input
        yield tok


if __name__ == '__main__':
    # Give the lexer some input
    f = open(sys.argv[1], 'r')
    for tok in run(f.read()):
        print(tok)
