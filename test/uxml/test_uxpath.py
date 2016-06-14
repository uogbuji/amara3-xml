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

#uxpath, doc element, result sequence
#Nodes in result are represented as a tuple of node name & concatenation of text node children
MAIN_CASES = [
    ('/', N1, [('', '')]),
    ('b', N1, [('b', '+2+')]),
    ('b/x', N1, [('x', '1')]),
    ('c/x', N1, [('x', '2')]),
]


@pytest.mark.parametrize('path,top,expected', MAIN_CASES)
def test_ts_gc(path, top, expected):
    ctx = context(top)
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
