# -----------------------------------------------------------------------------
# amara3.uxml.xmliter
#
# Iterator (generator and coroutine) facilities for MicroXML tree objects parsed from XML sources
#
# -----------------------------------------------------------------------------

import asyncio
import xml.parsers.expat

from . import treeiter
from .xml import expat_callbacks, ns_expat_callbacks


def buffer_handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return


'''
from asyncio import coroutine
from amara3.uxml import xml
@coroutine
def sink(accumulator):
    while True:
        e = yield
        accumulator.append(e.xml_value)

values = []
ts = xml.treesequence(('a', 'b'), sink(values))
ts.parse('<a xmlns="urn:namespaces:suck"><b>1</b><b>2</b><b>3</b></a>')
values

----

from asyncio import coroutine
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

ts = tree.treebuilder()
root = ts.parse('<a xmlns="urn:namespaces:suck"><b><c>1</c></b><b>2</b><b>3</b></a>')
pathresults = ppath(root, ('b', 'c'))
print(list(pathresults))
'''

class sender(treeiter.sender):
    '''
    >>> from amara3.uxml import xml
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ...
    >>> values = []
    >>> ts = xmliter.sender(('a', 'b'), sink(values))
    >>> ts.parse('<a xmlns="urn:namespaces:suck"><b>1</b><b>2</b><b>3</b></a>')
    >>> values
    ['1', '2', '3']
    '''
    def __init__(self, pattern, sink, callbacks=expat_callbacks):
        super(sender, self).__init__(pattern, sink)
        self.handler = callbacks(self._handler())
        self.expat_parser = xml.parsers.expat.ParserCreate(namespace_separator=' ')

        self.expat_parser.StartElementHandler = self.handler.start_element
        self.expat_parser.EndElementHandler = self.handler.end_element
        self.expat_parser.CharacterDataHandler = self.handler.char_data
        self.expat_parser.StartNamespaceDeclHandler = self.handler.start_namespace
        self.expat_parser.EndNamespaceDeclHandler = self.handler.end_namespace
        return

    def parse(self, source):
        self.expat_parser.Parse(source)
        return

    def parse_file(self, fp):
        self.expat_parser.ParseFile(fp)
        return
