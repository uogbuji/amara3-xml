'''
py.test test/uxml/test_tree.py
'''

import sys
import io
import logging

import pytest #Consider also installing pytest_capturelog
from amara3.uxml import tree
from amara3.uxml.tree import node, element
from amara3.uxml import html5


DOC1 = '<html><head><title>HELLO</title></head><body><p>WORLD</body></html>'
#DOC1 = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>HELLO</title></head><body><p>WORLD</body></html>'

#DOC_CASES = [DOC1, DOC2, DOC3, DOC4, DOC5]
DOC_CASES = [DOC1]


@pytest.mark.parametrize('doc', DOC_CASES)
def test_basic_nav(doc):
    root = html5.parse(io.StringIO(DOC1))
    logging.debug('root: {}'.format(repr(root)))
    #No parent
    assert root.xml_parent is None, (root, root.xml_parent)
    #Root is an element
    assert isinstance(root, element), root
    child_elems = [ ch for ch in root.xml_children if isinstance(root, element) ]
    for elem in child_elems:
        logging.debug('elem parent: {}'.format(repr(elem.xml_parent)))
        assert elem.xml_parent is root, (elem, root)


DOC2 = '<html><head><title>HELLO</title></head><body><p>WORLD<!--Comment--></body></html>'
DOC2_NORMALIZED = '<html><head><title>HELLO</title></head><body><p>WORLD<!--Comment--></p></body></html>'

def test_xml_encode_with_comment():
    root = html5.parse(io.StringIO(DOC2))
    logging.debug('root: {}'.format(repr(root)))
    # Round trip
    assert root.xml_encode() == DOC2_NORMALIZED


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
