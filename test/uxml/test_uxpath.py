'''
py.test test/uxml/test_treegc.py
'''

import sys
import gc

import pytest
from amara3.uxml import tree
from amara3.uxml.tree import node, text, element
from amara3.uxml.uxpath import context, parse as uxpathparse

#from amara3.util import coroutine

TB = tree.treebuilder()
P = TB.parse

N1 = P('<a>+1+<b i="1.1">+2+<x>1</x></b><c i="1.2"><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>')

N10 = P('<a><b>1</b><b>2</b><b>3</b></a>')
N11 = P('<a><b>1</b><c>2</c><d>3</d></a>')
N12 = P('<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>')
N13 = P('<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>')
N14 = P('<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>')

N14 = P('<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>')

V1 = {'a': 1, 'b': 'x', 'a1': N1, 'a1.2': N10}

#uxpath, doc element, result sequence
#Nodes in result are represented as a tuple of node name & concatenation of text node children
MAIN_CASES = [
    ('/', N1, [('', '')]),
    ('/a', N1, [('a', '+1+')]),
    #Does this absolute path still work if we shift context to b first?
    ('/', (N1, 'a/b'), [('', '')]),
    ('/a', (N1, 'a/b'), [('a', '+1+')]),

    ('b', N1, []),
    ('b/x', N1, []),
    ('b[x]', N1, []),
    ('a/b', N1, [('b', '+2+')]),
    ('a/b/x', N1, [('x', '1')]),
    ('a/b[x]', N1, [('b', '+2+')]),
    ('/a/b', N1, [('b', '+2+')]),
    ('/a/b/x', N1, [('x', '1')]),
    ('/a/b[x]', N1, [('b', '+2+')]),
    ('/a/c/d[x]', N1, [('d', '')]),
    ('/a/c[d/x]', N1, [('c', '')]),
    ('a/c/x', N1, [('x', '2')]),

    ('(a/b/x, a/c/x)', N1, [('x', '1'), ('x', '2')]),
]

SEQUENCE_CASES = [
    ('()', N1, []),
    ('(1, 2)', N1, [1, 2]),
    ('("a", "b", "c")', N1, ["a", "b", "c"]),
    ('(1, 2, 3, 4, 5)[. > 3]', N1, [4, 5]),
]

AXIS_CASES = [
    ('a/b[2]', N10, [('b', '2')]),
    ('a/b[2]/preceding-sibling::b', N10, [('b', '1')]),
    ('a/b[2]/preceding-sibling::*', N10, [('b', '1')]),
    ('a/b[1]/preceding-sibling::b', N10, []),
    ('a/b[1]/preceding-sibling::*', N10, []),
    ('a/b/preceding-sibling::b', N10, [('b', '1'), ('b', '2'), ('b', '1')]),
    ('a/b/preceding-sibling::*', N10, [('b', '1'), ('b', '2'), ('b', '1')]),
    ('a/b[2]/following-sibling::b', N10, [('b', '3')]),
    ('a/b[2]/following-sibling::*', N10, [('b', '3')]),
    ('a/b[3]/following-sibling::b', N10, []),
    ('a/b[3]/following-sibling::*', N10, []),
    ('a/b/following-sibling::b', N10, [('b', '2'), ('b', '3'), ('b', '3')]),
    ('a/b/following-sibling::*', N10, [('b', '2'), ('b', '3'), ('b', '3')]),
]

PREDICATE_CASES = [
    ('a/text()', N1, [('#text', '+1+')]),
    #('//*[starts-with(., "+")]', N1, [('a', '+1+'), ('b', '+2+')]),
    ('a[starts-with(., "+")]', N1, [('a', '+1+')]),
    ('a/b[starts-with(., "+")]', N1, [('b', '+2+')]),
    ('a[not(starts-with(., "+"))]', N1, []),
    ('a[contains(., "+")]', N1, [('a', '+1+')]),
    ('a/b[contains(., "+")]', N1, [('b', '+2+')]),
    ('a[not(contains(., "+"))]', N1, []),
]

FUNCTION_CASES = [
    ('count(a/b)', N14, [4]),
    ('for-each(a/b, "name(.)")', N14, ['b', 'b', 'b', 'b']),
    ('for-each(/a/b, "name(.)")', N14, ['b', 'b', 'b', 'b']),
    ('for-each(a/b, "name()")', N14, ['b', 'b', 'b', 'b']),
    ('for-each(a/b, "x")', N14, [('x', '1'), ('x', '2'), ('x', '3'), ('x', '4')]),
    ('for-each(a/b, "name(x)")', N14, ['x', 'x', 'x', 'x']),
    ('substring(a, 2, 1)', N1, ['1']),
]

TYPECAST_CASES = [
    ('boolean(a)', N1, [True]),
    ('boolean(a/b)', N1, [True]),
    ('boolean(x)', N1, [False]),
    ('boolean(x/y)', N1, [False]),
    ('number(a/c/x)', N1, [2.0]),
]

VAR_CASES = [
    ('$a', N1, [1]),
    ('$a1', N1, [('a', '+1+')]),
    ('$a1.2', N1, [('a', '')]),
    #('$a1/b', N1, [('a', '+1+')]),
    #('$a1.2/b', N1, [('a', '')]),
]


ALL_CASES = MAIN_CASES + SEQUENCE_CASES + AXIS_CASES + PREDICATE_CASES + \
    FUNCTION_CASES + TYPECAST_CASES + VAR_CASES
#@pytest.mark.parametrize('path,top,expected', AXIS_CASES)
@pytest.mark.parametrize('path,top,expected', ALL_CASES)
def test_expressions(path, top, expected):
    if isinstance(top, tuple):
        root, ctxfinder = top
    else:
        root, ctxfinder = top, None
    if ctxfinder:
        ctx = context(root, variables=V1)
        parsed_expr = uxpathparse(ctxfinder)
        root = next(parsed_expr.compute(ctx), None)
        assert root

    ctx = context(root, variables=V1)
    parsed_expr = uxpathparse(path)
    result = parsed_expr.compute(ctx)
    tresult = []
    for item in result:
        if isinstance(item, text):
            tresult.append((item.xml_name, item.xml_value))
        elif isinstance(item, node):
            s = ''.join([ t.xml_value for t in item.xml_children if isinstance(t, text) ])
            tresult.append((item.xml_name, s))
        else:
            tresult.append(item)
    assert tresult == expected, (tresult, expected)


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
