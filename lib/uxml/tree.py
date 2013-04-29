# -----------------------------------------------------------------------------
# amara3.uxml.tree
#
# Basic tree parser for MicroXML
# 
# -----------------------------------------------------------------------------

#See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

from amara3.uxml import lex

class element:
    def __init__(self, name, attrs=None, parent=None):
        self.xml_name = name
        self.xml_attrs = attrs or {}
        self.xml_parent = parent
        self.xml_children = []
        self._xml_build_attr_handler = None
        #self.ancestor_stack = [] # g_ancestor_stack
        return

    def build_attr(self, name):
        #if self._xml_build_attr == True:
        #    raise RuntimeError('Already started on an attribute definition')
        self.xml_attrs[name] = ''
        while True:
            valchunk = (yield)
            self.xml_attrs[name] += valchunk
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
    e._xml_within_attr_val = False
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
    return handle_unwrapped_chardata(value, parent)


def handle_unwrapped_chardata(value, parent):
    if parent._xml_build_attr_handler is None: # We'll violate encapsulation here, for now
        #We are in a state waiting for child nodes
        #TODO: for normalization check if prior child is also text & join if so
        parent.xml_children.append(value)
    else:
        #We are in a state waiting for an attribute value
        parent._xml_build_attr_handler.send(value)
    return parent


def handle_aname(tok, parent):
    aname = tok.value
    parent._xml_build_attr_handler = parent.build_attr(aname)
    next(parent._xml_build_attr_handler)
    return parent


def handle_quote(tok, parent):
    if parent._xml_within_attr_val: # We'll violate encapsulation here, for now
        #We are in a state waiting for an attribute value
        parent._xml_build_attr_handler.close()
        parent._xml_build_attr_handler = None
        parent._xml_within_attr_val = False
    else:
        parent._xml_within_attr_val = True
    return parent


#FIXME: a bit of currying here?
def handle_ampent(tok, parent):
    return handle_unwrapped_chardata('&', parent)


def handle_ltent(tok, parent):
    return handle_unwrapped_chardata('<', parent)


def handle_gtent(tok, parent):
    return handle_unwrapped_chardata('>', parent)


def handle_aposent(tok, parent):
    return handle_unwrapped_chardata("'", parent)


def handle_quotent(tok, parent):
    return handle_unwrapped_chardata('"', parent)


def handle_nument(tok, parent):
    #FIXME FIXME FIXME FIXME FIXME FIXME 
    return handle_unwrapped_chardata('&', parent)


TOKEN_HANDLERS = {
    'STARTTAG': handle_starttag,
    'ENDTAG': handle_endtag,
    'CHARDATA': handle_chardata,
    'NAME': handle_aname,
    'DBL_QUOTE': handle_quote,
    'AMP_ENT': handle_ampent,
    'LT_ENT': handle_ltent,
    'GT_ENT': handle_gtent,
    'APOS_ENT': handle_aposent,
    'QUOT_ENT': handle_quotent,
    'NUM_ENT': handle_nument,
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

