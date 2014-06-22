# -----------------------------------------------------------------------------
# amara3.uxml.tree
#
# Basic tree implementation for MicroXML
# 
# -----------------------------------------------------------------------------

#See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

from amara3.uxml.parser import parse, parser, parsefrags, event
from amara3.util import coroutine


class node(object):
    def xml_encode(self):
        raise ImplementationError

    def xml_write(self):
        raise ImplementationError


class element(node):
    def __init__(self, name, attrs=None, parent=None):#, ancestors=None):
        self.xml_name = name
        self.xml_attributes = attrs or {}
        self.xml_parent = parent
        self.xml_children = []
        #self.xml_ancestors = ancestors or []
        return

    def xml_encode(self):
        strbits = ['<', self.xml_name]
        for aname, aval in self.xml_attrs.items():
            strbits.extend([' ', aname, '="', aval, '"'])
        strbits.append('>')
        for child in self.xml_children:
            if isinstance(child, element):
                strbits.append(child.xml_encode())
            else:
                strbits.append(child)
        strbits.extend(['</', self.xml_name, '>'])
        return ''.join(strbits)

    @property
    def xml_value(self):
        return ''.join(map(lambda x: x.xml_value, self.xml_children))

    def __repr__(self):
        return u'<uxml.element ({0}) "{1}" with {2} children>'.format(hash(self), self.xml_name, len(self.xml_children))

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'

class text(node, str):
    def __new__(cls, value, parent):
        self = super(text, cls).__new__(cls, value)
        self.xml_parent = parent
        return self

    def __repr__(self):
        return u'<uxml.text "' + str(self)[:10] + '"...>'

    def xml_encode(self):
        return str(self)

    @property
    def xml_value(self):
        return str(self)

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'


class treebuilder(object):
    def __init__(self):
        self._root = None
        self._parent = None

    @coroutine
    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                new_element = element(ev[1], ev[2], self._parent)
                if self._parent: self._parent.xml_children.append(new_element)
                self._parent = new_element
                if not self._root: self._root = new_element
            elif ev[0] == event.characters:
                new_text = text(ev[1], self._parent)
                if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                if self._parent.xml_parent:
                    self._parent = self._parent.xml_parent
        return

    def parse(self, doc):
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return self._root
