# -----------------------------------------------------------------------------
# amara3.uxml.coax
#
# Coroutine API for (Micro)XML
#  A parser which sends MicroXML events to a coroutine
# -----------------------------------------------------------------------------

#See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

from amara3.uxml import lex

#Define the events
START_ELEMENT = 1
END_ELEMENT = 2
TEXT = 3


class element:
    def __init__(self, name, attrs=None, parent=None):
        self.xml_name = name
        self.xml_attrs = attrs or {}
        self.xml_parent = parent
        self.xml_children = []
        self._xml_partial_attr = None
        #self.ancestor_stack = [] # g_ancestor_stack
        return

    def set_attr_name(self, name):
        if self._xml_partial_attr is not None:
            raise RuntimeError('Already started on an attribute definition')
        self._xml_partial_attr = name
        return

    def build_attr_value(self, value):
        if self._xml_partial_attr is None:
            raise RuntimeError('Have not started on an attribute definition')
        if self._xml_partial_attr in self.xml_attrs:
            self.xml_attrs[self._xml_partial_attr] += value
        else:
            self.xml_attrs[self._xml_partial_attr] = value
        return

    def complete_attr_value(self):
        if self._xml_partial_attr is None:
            raise RuntimeError('Have not started on an attribute definition')
        self._xml_partial_attr = None
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

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'

def handle_starttag(tok, parent):
    ename = tok.value
    e = element(ename, parent=parent)
    return e


def handle_endtag(tok, parent):
    ename = tok.value
    #Parent name should thus match the end tag
    if parent.xml_name != ename:
        raise RuntimeError('End tag {0} does not match start tag {1}'.format((ename, parent.xml_name)))
    if parent.xml_parent is not None:
        new_parent = parent.xml_parent
        new_parent.xml_children.append(parent)
    else:
        #We have reached the root of the tree and so do not try to ascend
        #This is a major assymetry that should only occur at the end of parsing
        new_parent = parent
    return new_parent


def handle_chardata(tok, parent):
    value = tok.value
    if parent._xml_partial_attr is None: # We'll violate encapsulation here, for now
        #We are in a state waiting for child nodes
        #TODO: for normalization check if prior child is also text & join if so
        parent.xml_children.append(value)
    else:
        #We are in a state waiting for an attribute value
        parent.set_attr_value(value)
    return parent


def handle_aname(tok, parent):
    aname = tok.value
    parent.set_attr_name(aname)
    return parent


def handle_quote(tok, parent):
    if parent._xml_partial_attr is not None: # We'll violate encapsulation here, for now
        #We are in a state waiting for an attribute value
        parent.complete_attr_value()
    return parent


TOKEN_HANDLERS = {
    'STARTTAG': handle_starttag,
    'ENDTAG': handle_endtag,
    'CHARDATA': handle_chardata,
    'NAME': handle_aname,
    'DBL_QUOTE': handle_quote,
}


def run(s):
    parent = None
    for tok in lex.run(s):
        if tok.type in TOKEN_HANDLERS:
            parent = TOKEN_HANDLERS[tok.type](tok, parent)
        #yield tok
    return parent


if __name__ == '__main__':
    import sys
    # Give the lexer some input
    f = open(sys.argv[1], 'r')
    root = run(f.read())
    print(root.xml_encode())


def parse(ux, sink):
    return


'''
class element(object):
    def __init__(self, name, attrmap=None, children=None, ancestor_stack=None):
        self.name = name
        self.attrmap = attrmap
        self.children = children
        self.ancestor_stack = ancestor_stack

    def unparse(self):
        if children:
            return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>' + self.children.unparse() + '</' + self.name.encode('utf-8') + '>'
'''


class start_tag(object):
    def __init__(self, name, attrmap=None):
        self.name = name
        self.attrmap = attrmap
        self.ancestor_stack = g_ancestor_stack

    def unparse(self):
        return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'


class start_empty_tag(start_tag):
    def unparse(self):
        return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '/>'


class end_tag(object):
    def __init__(self, name, attrmap=None):
        self.name = name
        self.ancestor_stack = g_ancestor_stack

    def unparse(self):
        return '</' + self.name.encode('utf-8') + '>'


