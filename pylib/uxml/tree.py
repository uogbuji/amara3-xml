# -----------------------------------------------------------------------------
# amara3.uxml.tree
#
# Basic tree implementation for MicroXML
#
# -----------------------------------------------------------------------------

# See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

import sys
import weakref
from xml.sax.saxutils import escape, quoteattr

from amara3.uxml.parser import parser, event  # parse, parsefrags

# NO_PARENT = object()


class node:
    def __init__(self, parent=None):
        self._xml_parent = weakref.ref(parent) if parent is not None else None
        # self._xml_parent = weakref.ref(parent or NO_PARENT)
        self.xml_name = '' # to be overridden

    @property
    def xml_parent(self):
        return self._xml_parent() if self._xml_parent else None
        # p = self._xml_parent()
        # return None if p is NO_PARENT else p

    def xml_encode(self):
        raise NotImplementedError

    def xml_write(self, fp=sys.stdout):
        fp.write(self.xml_encode())

    def xml_xpath(self, xpath, vars=None, funcs=None):
        '''
        Execute an XPath query with this node as context item
    
        xpath - string or parsed XPath expression
        vars - optional mapping of variables, name to value
        funcs - optional mapping of functions, name to function object
    
        >>> from amara3.uxml.tree import parse
        >>> e = parse('<a>1<b>2</b>3</a>')
        >>> results = e.xml_xpath('a/text()')
        >>> next(results).xml_value
        '1'
        >>> next(results).xml_value
        '3'
        '''
        # In line to acoid circular import
        from amara3.uxml.uxpath import context as xpathcontext, parse as xpathparse
        force_root = not self.xml_parent

        if isinstance(xpath, str):
            xpath = xpathparse(xpath)
        elif not hasattr(xpath, 'compute'):
            raise ValueError('XPath argument must be an expression string or a parsed expression object')

        ctx = xpathcontext(self, variables=vars, functions=funcs, force_root=force_root)
        result = xpath.compute(ctx)
        yield from result


class element(node):
    '''
    Note: Meant to be bare bones & Pythonic. Does no integrity checking of direct manipulations, such as adding an integer to xml_children, or '1' as an attribute name
    '''
    def __init__(self, name, attrs=None, parent=None):#, ancestors=None):
        node.__init__(self, parent)
        self.xml_name = name
        self.xml_attributes = attrs or {}
        self.xml_children = []
        return

    def xml_encode(self, indent=None, depth=0):
        '''
        Unparse an object back to XML text, returning the string object

        >>> from amara3.uxml.tree import parse
        >>> e = parse('<a>bc&amp;de</a>')
        >>> e.xml_encode()
        '<a>bc&amp;de</a>'
        '''
        strbits = ['<', self.xml_name]
        for aname, aval in self.xml_attributes.items():
            strbits.extend([' ', aname, '=', quoteattr(aval)])
        strbits.append('>')
        if indent:
            strbits.append('\n')
            strbits.append(indent*depth)
        for child in self.xml_children:
            if isinstance(child, element):
                strbits.append(child.xml_encode(indent=indent, depth=depth+1))
                if indent:
                    strbits.append('\n')
                    strbits.append(indent*depth)
            elif isinstance(child, str):
                strbits.append(escape(child))
            else:
                strbits.append(child.xml_encode())
        strbits.extend(['</', self.xml_name, '>'])
        return ''.join(strbits)

    # What's the difference from strval?
    @property
    def xml_value(self):
        '''
        Accumulated text in all descendant elements (similar to XPath text value)
        '''
        # Recursive action
        return ''.join(map(lambda x: x.xml_value, self.xml_children))

    #Really just an alias that forbids specifying position
    def xml_append(self, child):
        '''
        Append a node as the last child

        child - the child to append. If a string, convert to a text node, for convenience
        '''
        self.xml_insert(child)
        return

    def xml_insert(self, child, index=-1):
        '''
        Append a node as the last child

        child - the child to append. If a string, convert to a text node, for convenience
        '''
        if isinstance(child, str):
            child = text(child, parent=self)
        else:
            child._xml_parent = weakref.ref(self)
        if index == -1:
            self.xml_children.append(child)
        else:
            self.xml_children.insert(index, child)
        return

    def xml_remove(self, child: node):
        '''
        Remove a child element. Does not destroy the child element, which becomes
        the new root of its own tree

        child - the child to remove
        '''
        if child in self.xml_children:
            child._xml_parent = None
            self.xml_children.remove(child)
        else:
            raise ValueError(f'Element {self} has no child {child}')
        return

    def __repr__(self):
        return u'{{uxml.element ({0}) "{1}" with {2} children}}'.format(hash(self), self.xml_name, len(self.xml_children))

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'

class text(node, str):
    def __new__(cls, value, parent=None):
        self = super(text, cls).__new__(cls, value)
        return self

    def __init__(self, value, parent=None):#, ancestors=None):
        node.__init__(self, parent)
        self.xml_name = '#text'
        return

    def __repr__(self):
        return u'{{uxml.text "{}"...}}'.format(str(self)[:10])

    def xml_encode(self, indent=None, depth=0):
        return str(self)

    @property
    def xml_value(self):
        return str(self)

    @property
    def xml_children(self):
        return []

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'


def strval(node, outermost=True):
    '''
    XPath-like string value of node
    '''
    if not isinstance(node, element):
        return node.xml_value if outermost else [node.xml_value]
    accumulator = []
    for child in node.xml_children:
        if isinstance(child, text):
            accumulator.append(child.xml_value)
        elif isinstance(child, element):
            accumulator.extend(strval(child, outermost=False))
    if outermost: accumulator = ''.join(accumulator)
    return accumulator


class treebuilder(object):
    def __init__(self):
        self._root = None
        self._parent = None

    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                new_element = element(ev[1], ev[2], self._parent)
                #Note: not using weakrefs here because these refs are not circular
                if self._parent: self._parent.xml_children.append(new_element)
                self._parent = new_element
                #Hold a reference to the top element of the subtree being built,
                #or it will be garbage collected as the builder moves down the tree
                if not self._root: self._root = new_element
            elif ev[0] == event.characters:
                new_text = text(ev[1], self._parent)
                if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                if self._parent:
                    self._parent = self._parent.xml_parent
        return

    def parse(self, doc):
        #reset
        self._root = None
        self._parent = None
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return self._root


def name_test(name):
    def _name_test(ev):
        return ev[0] == event.start_element and ev[1] == name
    return _name_test


def elem_test():
    def _elem_test(ev):
        return ev[0] == event.start_element
    return _elem_test


def parse(doc):
    return treebuilder().parse(doc)


'''
from amara3.uxml import tree
from amara3.uxml.treeutil import *

def ppath(start, path):
    print((start, path))
    if not path: return None
    if len(path) == 1:
        yield from select_name(start, path[0])
    else:
        for e in select_name(start, path[0]):
            yield from ppath(e, path[1:])

root = tree.parse('<a xmlns="urn:namespaces:suck"><b><c>1</c></b><b>2</b><b>3</b></a>')
pathresults = ppath(root, ('b', 'c'))
print(list(pathresults))
'''

