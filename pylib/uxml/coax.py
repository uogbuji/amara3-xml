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


