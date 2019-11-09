########################################################################
# amara3.uxml.html
"""

"""

__all__ = [
'node', 'treebuilder', 'comment', 'element',
]

import copy
import itertools
import weakref

from . import tree
from . import treeiter
from .treeutil import *
#from . import xmliter

try:
    import html5lib
    from html5lib.treebuilders.base import TreeBuilder, Node
except ImportError:
    raise


class node(Node):
    parent = tree.element.xml_parent
    value = tree.text.xml_value

    def appendChild(self, node):
        self.xml_append(node)

    def removeChild(self, node):
        self.xml_children.remove(node)

    def insertText(self, data, insertBefore=None):
        """Insert data as text in the current node, positioned before the
        start of node insertBefore or to the end of the node's text.
        """
        if insertBefore:
            self.insertBefore(tree.text(data), insertBefore)
        else:
            self.xml_append(tree.text(data))

    def insertBefore(self, node, refNode):
        """Insert node as a child of the current node, before refNode in the
        list of child nodes. Raises ValueError if refNode is not a child of
        the current node"""
        offset = self.xml_children.index(refNode)
        self.xml_insert(node, offset)

    def cloneNode(self):
        """Return a shallow copy of the current node i.e. a node with the same
        name and attributes but with no parent or child nodes
        """
        raise NotImplementedError

    def hasContent(self):
        """Return true if the node has children or text, false otherwise
        """
        return bool(self.xml_children)


def qname_to_local(qname):
    return qname.split(':')[-1]


class element(tree.element, node):
    '''
    attributes - a dict holding name, value pairs for attributes of the node
    childNodes - a list of child nodes of the current node. This must
    include all elements but not necessarily other node types
    _flags - A list of miscellaneous flags that can be set on the node
    '''
    #name = nodes.element_base.xml_qname
    #namespace = nodes.element_base.xml_namespace
    #xml_exclude_pnames = frozenset(('name', 'parent', 'appendChild', 'removeChild', 'removeChild', 'value', 'attributes', 'childNodes'))
    @property
    def name(self):
        return getattr(self, 'xml_html5lib_name', self.xml_name)

    @property
    def namespace(self):
        return getattr(self, 'xml_html5lib_namespace', None)

    @property
    def nameTuple(self):
        name = getattr(self, 'xml_html5lib_name', self.xml_name)
        namespace = getattr(self, 'xml_html5lib_namespace', None)
        return namespace, name
        #return XHTML_NAMESPACE, self.xml_name

    def xml_get_childNodes_(self):
        return self.xml_children

    def xml_set_childNodes_(self, nodelist):
        self.xml_children = []
        for node in nodelist:
            self.xml_append(node)
        return

    childNodes = property(xml_get_childNodes_, xml_set_childNodes_, None, "html5lib uses this property to manage HTML element children")

    def __init__(self, name, attrs=None):
        tree.element.__init__(self, name, attrs)
        self._flags = []
        return

    def xml_set_attributes_(self, attrs):
        for key, val in attrs.items():
            if isinstance(key, tuple):
                self.xml_attributes[qname_to_local(key[1])] = val
            elif key.startswith(u'xmlns'):
                continue
            else:
                self.xml_attributes[key] = val
        return

    def xml_get_attributes_(self):
        return self.xml_attributes

    attributes = property(xml_get_attributes_, xml_set_attributes_, None, "html5lib uses this property to manage HTML element attrs")

    def cloneNode(self):
        """Return a shallow copy of the current node i.e. a node with the same
        name and attributes but with no parent or child nodes
        """
        attrs = self.xml_attributes.copy()
        return element(self.xml_name, attrs=attrs)


#class comment(tree.comment):
class comment(object):
    type = 6
    value = tree.text.xml_value
    def __init__(self, data):
        self.data = data
        return

    def toxml(self):
        return "<!--%s-->" % self.data

#Note: element = 6

class document(object):
    type = 9
    def __init__(self):
        self.root_nodes = []
        return

    def appendChild(self, node):
        self.root_nodes.append(node)

    def toxml(self):
        return "<!--%s-->" % self.data


class doctype(object):
    type = 10
    def __init__(self, name, publicId, systemId):
        self.name = name
        self.publicId = publicId
        self.systemId = systemId
        return

    def toxml(self):
        return "<!--%s-->" % self.data


MARKER = object()

BOGUS_NAMESPACE = u'urn:bogus:x'
NAME_FOR_ELEMENTS_UNNAMED_BY_HTML5LIB = u'UNNAMED_BY_HTML5LIB'
XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'

class treebuilder(TreeBuilder):
    commentClass = comment
    documentClass = document
    #def __init__(self, entity_factory=None, use_xhtml_ns=False):
    #    self.entity = entity_factory()
    #def documentClass(self):
    #    return weakref.proxy(self)

    def doctypeClass(self, name, publicId, systemId):
        attrs = {'html5.publicId': publicId, 'html5.systemId': systemId}
        return tree.element(name, attrs=attrs)

    def __init__(self, use_xhtml_ns=False):
        self.root_nodes = []
        #html5lib.treebuilders._base.TreeBuilder breaks if you do not pass in True for namespaceHTMLElements
        #We'll take care of that ourselves with the if not use_xhtml_ns... below
        TreeBuilder.__init__(self, True)
        def eclass(name, namespace):
            xml_html5lib_name, xml_html5lib_namespace = MARKER, MARKER
            if not use_xhtml_ns and namespace == XHTML_NAMESPACE:
                #html5lib feints support for HTML5 elements kept in the null namespace
                #But in reality this support is broken.  We have to in effect keep
                #Two namespaces for each element, the real one from an amara perspective
                #And another that is always XHTML for HTML5 elements, so html5lib doesn't break
                xml_html5lib_namespace = namespace
                namespace = None
            #For some reason html5lib sometimes sends None as name
            if not name:
                xml_html5lib_name = name
                name = NAME_FOR_ELEMENTS_UNNAMED_BY_HTML5LIB
            #import sys; print >> sys.stderr, (namespace, name, use_xhtml_ns)
            #Deal with some broken HTML that uses bogus colons in tag names
            if (u":" in name and not namespace):
                xml_html5lib_namespace = namespace
                namespace = BOGUS_NAMESPACE
            elem = element(qname_to_local(name))
            if xml_html5lib_namespace != MARKER:
                elem.xml_html5lib_namespace = xml_html5lib_namespace
            if xml_html5lib_name != MARKER:
                elem.xml_html5lib_name = xml_html5lib_name
            return elem
        self.elementClass = eclass
        self.fragmentClass = eclass


'''
from amara3.uxml import html5
import urllib.request
with urllib.request.urlopen('http://uche.ogbuji.net/') as response:
    e = html5.parse(response)
'''


def parse(source, prefixes=None, model=None, encoding=None, use_xhtml_ns=False):
    '''
    Parse an input source with HTML text into an Amara 3 tree

    >>> from amara3.uxml import html5
    >>> import urllib.request
    >>> with urllib.request.urlopen('http://uche.ogbuji.net/') as response:
    ...     html5.parse(response)


    #Warning: if you pass a string, you must make sure it's a byte string, not a Unicode object.  You might also want to wrap it with amara.lib.inputsource.text if it's not obviously XML or HTML (for example it could be confused with a file name)
    '''
    def get_tree_instance(namespaceHTMLElements, use_xhtml_ns=use_xhtml_ns):
        #use_xhtml_ns is a boolean, whether or not to use http://www.w3.org/1999/xhtml
        return treebuilder(use_xhtml_ns)
    parser = html5lib.HTMLParser(tree=get_tree_instance)
    #doc = parser.parse(inputsource(source, None).stream, encoding=encoding)
    #doc = parser.parse(source, encoding=encoding)
    doc = parser.parse(source)
    first_element = next((e for e in doc.root_nodes if isinstance(e, element)), None)
    return first_element


def markup_fragment(source, encoding=None):
    '''
    Parse a fragment of markup in HTML mode, and return a tree node

    Warning: if you pass a string, you must make sure it's a byte string, not a Unicode object.  You might also want to wrap it with amara.lib.inputsource.text if it's not obviously XML or HTML (for example it could be confused with a file name)

    from amara.lib import inputsource
    from amara.bindery import html
    doc = html.markup_fragment(inputsource.text('XXX<html><body onload="" color="white"><p>Spam!<p>Eggs!</body></html>YYY'))

    See also: http://wiki.xml3k.org/Amara2/Tagsoup
    '''
    doc = parse(source, encoding=encoding)
    frag = doc.html.body
    return frag

