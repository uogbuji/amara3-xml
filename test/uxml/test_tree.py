'''
py.test test/uxml/test_tree.py
'''

import sys
import logging
from asyncio import coroutine

import pytest #Consider also installing pytest_capturelog
from amara3.uxml import tree
from amara3.uxml.tree import node, element


DOC1 = '<a><b>1</b><b>2</b><b>3</b></a>'
DOC2 = '<a><b>1</b><c>2</c><d>3</d></a>'
DOC3 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>'
DOC4 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'
DOC5 = '<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>'

DOC_CASES = [DOC1, DOC2, DOC3, DOC4, DOC5]


@pytest.mark.parametrize('doc', DOC_CASES)
def test_basic_nav(doc):
    tb = tree.treebuilder()
    root = tb.parse(doc)
    #No parent
    assert root.xml_parent is None
    #Root is an element
    assert isinstance(root, element)
    child_elems = [ ch for ch in root.xml_children if isinstance(root, element) ]
    for elem in child_elems:
        assert elem.xml_parent is root


@pytest.mark.parametrize('doc', DOC_CASES)
def test_basic_mutate(doc):
    tb = tree.treebuilder()
    root = tb.parse(doc)
    new_elem_1 = element('dee', {'a': '1'})
    root.xml_append(new_elem_1)
    new_elem_2 = element('dum', {'a': '2'})
    root.xml_insert(new_elem_2, 0)
    #logging.debug(root.xml_children)
    assert root.xml_children[-1] == new_elem_1, (root.xml_children[-1], new_elem_1)
    assert root.xml_children[0] == new_elem_2, (root.xml_children[0], new_elem_2)
    #FIXME: More testing


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
