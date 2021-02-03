# amara3.uxml.uxpath

'''
from amara3.uxml.uxpath import qquery
results = qquery(b'<a>1<b>2</b>3</a>', 'a/text()'))
next(results).xml_value
next(results).xml_value


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
from amara3.uxml import tree
from amara3.uxml.treeutil import *
from amara3.uxml.tree import node as nodetype
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

parser = yacc.yacc(module=parserules, outputdir=parsedir)#, debug=True)


def parse(xpath):
    '''
    Parse an xpath.
    
    >>> from amara3.uxml.uxpath import parse
    >>> xp = parse('a/text()')
    '''
    # Explicitly specify the lexer created above, otherwise parser.parse will use the most-recently created lexer. (Ewww! Wha?!)
    return parser.parse(xpath, lexer=lexer)#, debug=True)


class context(object):
    def __init__(self, item, pos=None, variables=None, functions=None, lookuptables=None, extras=None, parent=None, force_root=True):
        '''
        
        Note: No explicit context size. Will be dynamically computed if needed
        '''
        self.item = item
        if force_root and isinstance(item, nodetype):
            self.item = ast.root_node.get(item)
        self.pos = pos
        self.variables = variables or {}
        self.functions = functions or BUILTIN_FUNCTIONS
        self.extras = extras or {}
        #Needed for the case where the context node is a text node
        self.parent = parent or nodetype.xml_parent
        self.lookuptables = lookuptables or {}

    def copy(self, item=None, pos=None, variables=None, functions=None, lookuptables=None, extras=None, parent=None):
        item = item if item else self.item
        pos = pos if pos else self.pos
        variables = variables if variables else self.variables
        functions = functions if functions else self.functions
        lookuptables = lookuptables if lookuptables else self.lookuptables
        extras = extras if extras else self.extras
        parent = parent if parent else self.parent
        return context(item, pos=pos, variables=variables, functions=functions, lookuptables=lookuptables, extras=extras, parent=parent, force_root=False)


def qquery(xml_thing, xpath_thing, vars=None, funcs=None, force_root=True):
    '''
    Quick query. Convenience for using the MicroXPath engine.
    Give it some XML and an expression and it will yield the results. No fuss.
    
    xml_thing - bytes or string, or amara3.xml.tree node
    xpath_thing - string or parsed XPath expression
    vars - optional mapping of variables, name to value
    funcs - optional mapping of functions, name to function object
    
    >>> from amara3.uxml.uxpath import qquery
    >>> results = qquery(b'<a>1<b>2</b>3</a>', 'a/text()'))
    >>> next(results).xml_value
    '1'
    >>> next(results).xml_value
    '3'
    '''
    root = None
    if isinstance(xml_thing, nodetype):
        root = xml_thing
    elif isinstance(xml_thing, str):
        tb = tree.treebuilder()
        root = tb.parse(xml_thing)
    elif isinstance(xml_thing, bytes):
        tb = tree.treebuilder()
        #Force UTF-8
        root = tb.parse(xml_thing.decode('utf-8'))
    if not root: return
    if isinstance(xpath_thing, str):
        parsed_expr = parse(xpath_thing)
    ctx = context(root, variables=vars, functions=funcs, force_root=force_root)
    result = parsed_expr.compute(ctx)
    yield from result

