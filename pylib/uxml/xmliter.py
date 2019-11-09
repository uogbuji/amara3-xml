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


class sender(treeiter.sender):
    '''
    >>> from amara3.uxml import xmliter
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
    def __init__(self, pattern, sink, prime_sinks=True, callbacks=expat_callbacks):
        super(sender, self).__init__(pattern, sink, prime_sinks=prime_sinks)
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
