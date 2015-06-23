'''
py.test test/uxml/test_treegc.py
'''

import sys
import gc

import pytest
from amara3.uxml import tree
from amara3.uxml.treeutil import *
#from amara3.util import coroutine

DOC1 = '<a><b>1</b><b>2</b><b>3</b></a>'
DOC2 = '<a><b>1</b><c>2</c><d>3</d></a>'
DOC3 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>'
DOC4 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'
DOC5 = '<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>'

MAKEPRETTY_CASES = [
    (DOC4, 0, '  ', '<a>\n  <b>\n    <x>1</x>\n  </b>\n  <c>\n    <x>2</x>\n    <d>\n      <x>3</x>\n    </d>\n  </c>\n  <x>4</x>\n  <y>5</y>\n</a>'),
]


@pytest.mark.parametrize('doc,dep,ind,expected', MAKEPRETTY_CASES)
def test_ts_gc(doc, dep, ind, expected):
    tb = tree.treebuilder()
    root = tb.parse(doc)
    make_pretty(root, dep, ind)
    assert root.xml_encode() == expected


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
