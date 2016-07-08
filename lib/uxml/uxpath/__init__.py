# amara3.uxml.uxpath

'''
from amara3.uxml import tree
DOC = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'
tb = tree.treebuilder()
root = tb.parse(DOC)
from amara3.uxml.uxpath import context, parse as uxpathparse
ctx = context(root)
parsed_expr = uxpathparse('b/x')
result = parsed_expr.compute(ctx)
print(result)
print(list(result))
'''

import os
import re
import tempfile

from ply import lex, yacc

#from amara3 import iri
#from amara3.uxml import xml
from amara3.uxml.treeutil import *
from amara3.util import coroutine
from . import lexrules, parserules, ast
from .functions import BUILTIN_FUNCTIONS

__all__ = ['lexer', 'parser', 'parse', 'context']#, 'serialize']


lexer = None
#BUILDuxpath.LEX=1; python -m amara3.uxml.uxpath
if 'BUILDuxpath.LEX' in os.environ:
    # Build with cached lex table. Meant for developers to do and commit the updated file. Will fail without write access on the source directory.
    lexdir = os.path.dirname(lexrules.__file__)
    try:
        lexer = lex.lex(module=lexrules, optimize=1, outputdir=lexdir,
            reflags=re.UNICODE)
    except IOError as e:
        import errno
        if e.errno != errno.EACCES:
            raise

if lexer is None:
    lexer = lex.lex(module=lexrules, reflags=re.UNICODE)

# Generate parsetab.py 
parsedir = os.path.dirname(parserules.__file__)
if (not os.access(parsedir, os.W_OK)):
    parsedir = tempfile.gettempdir()

parser = yacc.yacc(module=parserules, outputdir=parsedir, debug=0)


def parse(xpath):
    '''Parse an xpath.'''
    # Explicitly specify the lexer created above, otherwise parser.parse will use the most-recently created lexer. (Ewww! Wha?!)
    return parser.parse(xpath, lexer=lexer) #, debug=True)


class context(object):
    def __init__(self, node, nodeseq=None, variables=None, functions=None, extras=None, parent=None, force_root=True):
        '''
        '''
        self.node = node
        if force_root and not node.xml_parent:
            self.node = ast.root_node.get(node)
        self.nodeseq = nodeseq or iter([node])
        self.variables = variables or {}
        self.functions = functions or BUILTIN_FUNCTIONS
        self.extras = extras or {}
        #Needed for the case where the context node is a text node
        self.parent = parent or node.xml_parent

    def copy(self, node=None, nodeseq=None, variables=None, functions=None, extras=None, parent=None):
        node = node if node else self.node
        nodeseq = nodeseq if nodeseq else self.nodeseq
        variables = variables if variables else self.variables
        functions = functions if functions else self.functions
        extras = extras if extras else self.extras
        parent = parent if parent else self.parent
        return context(node=node, nodeseq=nodeseq, variables=variables, functions=functions, extras=extras, parent=parent, force_root=False)


def xpathish_pattern_translator(pat):

    return 
