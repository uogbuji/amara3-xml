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

N1 = P('''<a>+1+<b i="1.1">+2+<x>1</x></b><c i="1.2"><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>''')

N10 = P('<a><b>1</b><b>2</b><b>3</b></a>')
N11 = P('<a><b>1</b><c>2</c><d>3</d></a>')
N12 = P('<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>')
N13 = P('<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>')
N14 = P('<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>')

V1 = {'a': 1, 'b': 'x', 'a1': N1, 'a1.2': N10}

#uxpath, doc element, result sequence
#Nodes in result are represented as a tuple of node name & concatenation of text node children
MAIN_CASES = [
    ('/', N1, [('', '')]),
    ('/a', N1, [('a', '+1+')]),
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
]

VAR_CASES = [
    ('$a', N1, [1]),
    ('$a1', N1, [('a', '+1+')]),
    ('$a1.2', N1, [('a', '')]),
    #('$a1/b', N1, [('a', '+1+')]),
    #('$a1.2/b', N1, [('a', '')]),
]


@pytest.mark.parametrize('path,top,expected', MAIN_CASES+SEQUENCE_CASES+VAR_CASES)
def test_ts_gc(path, top, expected):
    ctx = context(top, variables=V1)
    parsed_expr = uxpathparse(path)
    result = parsed_expr.compute(ctx)
    tresult = []
    for item in result:
        if isinstance(item, node):
            s = ''.join([ t.xml_value for t in item.xml_children if isinstance(t, text) ])
            tresult.append((item.xml_name, s))
        else:
            tresult.append(item)
    assert tresult == expected, (tresult, expected)


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
