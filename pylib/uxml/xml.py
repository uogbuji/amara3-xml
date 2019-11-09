# -----------------------------------------------------------------------------
# amara3.uxml.xml
#
# MicroXML tree objects parsed from XML sources
#
# -----------------------------------------------------------------------------

import asyncio
import xml.parsers.expat
from xml.sax.saxutils import escape  # also quoteattr?

from . import tree
from .parser import parser, parsefrags, event


class expat_callbacks(object):
    def __init__(self, handler, prime_handler=True):
        self._handler = handler
        self._elem_stack = []
        #if asyncio.iscoroutine(handler):
        if prime_handler:
            next(handler)  # Prime coroutine
        return

    def start_element(self, name, attrs):
        #print('Start element:', name, attrs)
        local = name.split()[-1]
        #print(attrs, name)
        new_attrs = {}
        for aname, aval in attrs.items():
            new_attrs[aname.split()[-1]] = aval
        self._handler.send((event.start_element, local, new_attrs, self._elem_stack.copy()))
        self._elem_stack.append(local)

    def end_element(self, name):
        #print('End element:', name)
        local = name.split()[1] if ' ' in name else name
        self._elem_stack.pop()
        self._handler.send((event.end_element, local, self._elem_stack.copy()))

    def char_data(self, data):
        #print('Character data:', repr(data))
        self._handler.send((event.characters, data))

    def start_namespace(self, prefix, ns):
        pass

    def end_namespace(self, prefix):
        pass


class ns_expat_callbacks(expat_callbacks):
    def __init__(self, handler, asyncio_based_handler=True, stream=False):
        expat_callbacks.__init__(self, handler, asyncio_based_handler=asyncio_based_handler)
        #Namespace mappings encountered through the document, updated dynamically as the document is traversed
        self.prefixes = {}
        self.prefixes_rev = {}
        #If True, state of NS mappings will be maintained dynamically, as suitable to streaming mode parse operation
        #If false, best effort will be made to maintain a cumulative mapping of namespaces declared
        #For best results always use namespace normal form:
        # http://www.ibm.com/developerworks/library/x-namcar/
        self._stream = stream
        #Heuristic structure suggesting output namespaces to generate
        #element: (prefix, namespace)
        self.ns_portfolio = {}
        return

    def start_namespace(self, prefix, ns):
        self.prefixes[prefix] = ns
        self.prefixes_rev[ns] = prefix

    def end_namespace(self, prefix):
        if self._stream: del self.prefixes[prefix]

    def start_element(self, name, attrs):
        #print('Start element:', name, attrs)
        ns, local = name.split() if ' ' in name else (None, name)
        if local not in self.ns_portfolio:
            self.ns_portfolio[local] = (ns, self.prefixes_rev[ns])
        for aname, aval in attrs.items():
            ans, alocal = aname.split() if ' ' in aname else (None, aname)
            self.ns_portfolio['@' + alocal] = (ans, self.prefixes_rev.get(ans, ''))
        expat_callbacks.start_element(self, name, attrs)


def parse(source, handler):
    '''
    Convert XML 1.0 to MicroXML

    source - XML 1.0 input
    handler - MicroXML events handler

    Returns uxml, extras

    uxml - MicroXML element extracted from the source
    extras - information to be preserved but not part of MicroXML, e.g. namespaces
    '''
    h = expat_callbacks(handler)
    p = xml.parsers.expat.ParserCreate(namespace_separator=' ')

    p.StartElementHandler = h.start_element
    p.EndElementHandler = h.end_element
    p.CharacterDataHandler = h.char_data
    p.StartNamespaceDeclHandler = h.start_namespace
    p.EndNamespaceDeclHandler = h.end_namespace
    p.Parse(source)
    return p


# Tree-based tools

class treebuilder(tree.treebuilder):
    '''
    from amara3.uxml import xml

    b = xml.treebuilder()
    root = b.parse('<spam/>')
    root
    '''
    def parse(self, source):
        self.handler = expat_callbacks(self._handler())
        self.expat_parser = xml.parsers.expat.ParserCreate(namespace_separator=' ')

        self.expat_parser.StartElementHandler = self.handler.start_element
        self.expat_parser.EndElementHandler = self.handler.end_element
        self.expat_parser.CharacterDataHandler = self.handler.char_data
        self.expat_parser.StartNamespaceDeclHandler = self.handler.start_namespace
        self.expat_parser.EndNamespaceDeclHandler = self.handler.end_namespace
        self.expat_parser.Parse(source)
        return self._root

