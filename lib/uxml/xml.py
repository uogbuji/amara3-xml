#import asyncio
import xml.parsers.expat

from amara3.uxml import tree
from amara3.uxml.parser import parse, parser, parsefrags, event
from amara3.util import coroutine

class expat_callbacks(object):
    def __init__(self, handler, asyncio_based_handler=True):
        self._handler = handler
        self._elem_stack = []
        if asyncio_based_handler:
            next(self._handler) #Start the coroutine running
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


@coroutine
def buffer_handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return


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
    p.Parse(source)
    return


#XXX Ignore the following for now
class strip(object):
    '''
    Policy for parsing legacy XML that strips all information from the MicroXML result
    '''
    def __init__(self):
        return


def expat_callbacks_(source, handler, policy=strip()):
    '''
    Policy-aware expat callbacks for parsing XML 1.x and emitting MicroXML

    source - XML 1.0 input
    handler - MicroXML events handler

    Returns uxml, extras

    uxml - MicroXML element extracted from the source
    extras - information to be preserved but not part of MicroXML, e.g. namespaces
    '''
    estack = []
    #extras = {}
    nss = {}
    parent = None

    def start_element(name, attrs):
        name = nsstrip(name)
        attrs = nsstrip_attrs(attrs)
        e = tree.element(name, attrs, parent)
        estack.append(e)
        parent = e

    def end_element(name):
        name = nsstrip(name)
        assert name == parent.xml_name == estack[-1].xml_name

    def char_data(data):
        estack[-1].xml_children.append(data)

    def nsstrip(name):
        name_parts = name.split()
        if len(name_parts) == 2:
            ns, name = name_parts

    #return uxml, extras

