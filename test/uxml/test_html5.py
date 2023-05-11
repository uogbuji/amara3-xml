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
from amara3.uxml.uxpath import qquery


DOC1 = '<html><head><title>HELLO</title></head><body><p>WORLD</body></html>'
# DOC1 = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>HELLO</title></head><body><p>WORLD</body></html>'


# DOC_CASES = [DOC1, DOC2, DOC3, DOC4, DOC5]
DOC_CASES = [DOC1]


@pytest.mark.parametrize('doc', DOC_CASES)
def test_basic_nav(doc):
    root = html5.parse(io.StringIO(DOC1))
    logging.debug('root: {}'.format(repr(root)))
    # No parent
    assert root.xml_parent is None, (root, root.xml_parent)
    # Root is an element
    assert isinstance(root, element), root
    child_elems = [ ch for ch in root.xml_children if isinstance(root, element) ]
    for elem in child_elems:
        logging.debug('elem parent: {}'.format(repr(elem.xml_parent)))
        assert elem.xml_parent is root, (elem, root)


DOC2 = '<html><head><title>HELLO</title></head><body><p>WORLD<!--Comment--></body></html>'
# Note removal of comment
DOC2_NORMALIZED = '<html><head><title>HELLO</title></head><body><p>WORLD</p></body></html>'


def test_xml_encode_with_comment():
    root = html5.parse(io.StringIO(DOC2))
    logging.debug('root: {}'.format(repr(root)))
    # Round trip
    assert root.xml_encode() == DOC2_NORMALIZED


DOC_NON_WF_XML = '<a x=1><b>Spam</b>'
DOC_NON_WF_XML_NORM = '<a x="1"><b>Spam</b></a>'


def test_non_wf_xml_parse():
    root = html5.parse_lax_xml(io.StringIO(DOC_NON_WF_XML))
    # Round trip
    assert root.xml_encode() == DOC_NON_WF_XML_NORM


DOC3 = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="description" content="Simple HTML">
      <title>Example</title></head>
  <body>
    <!-- Just a para in the world -->
    <!-- Spans demo no end tag -->
    <p class="plain"><span>Ndewonu! <span>This is HTML.</p>
  </body>
</html>
'''
# Notice how the span nesting is inferred (perhaps counter-intuitively)
DOC3_NORMALIZED = '''<html><head>
    <meta charset="UTF-8"></meta>
    <meta name="description" content="Simple HTML"></meta>
      <title>Example</title></head>
  <body>
    
    
    <p class="plain"><span>Ndewonu! <span>This is HTML.</span></span></p>
  

</body></html>'''


def test_top_doctring_example():
    html_el = html5.parse(DOC3)
    logging.debug('html_el: {}'.format(repr(html_el)))
    # Round trip
    assert html_el.xml_encode() == DOC3_NORMALIZED
    # Tree traversal
    p_elems = list(qquery(html_el, '/html//p'))
    assert len(p_elems) == 1


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
