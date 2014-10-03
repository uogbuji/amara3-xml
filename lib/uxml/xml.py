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


#Tree-based tools

class treebuilder(tree.treebuilder):
    '''
    b = xtb()
    root = b.parse('<spam/>')
    root
    '''
    def parse(self, source):
        expat_handler = expat_reader(self._handler(), asyncio_based_handler=False)
        p = xml.parsers.expat.ParserCreate(namespace_separator=' ')

        p.StartElementHandler = expat_handler.start_element
        p.EndElementHandler = expat_handler.end_element
        p.CharacterDataHandler = expat_handler.char_data
        p.Parse(source)

        return self._root


'''
from amara3.uxml import xml
from amara3.util import coroutine
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

from amara3.uxml import tree
from amara3.util import coroutine
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

class treesequence(tree.treesequence):
    '''
    >>> from amara3.uxml import xml
    >>> from amara3.util import coroutine
    >>> @coroutine
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ... 
    >>> values = []
    >>> ts = xml.treesequence(('a', 'b'), sink(values))
    >>> ts.parse('<a xmlns="urn:namespaces:suck"><b>1</b><b>2</b><b>3</b></a>')
    >>> values
    ['1', '2', '3']
    '''
    def parse(self, source):
        h = expat_callbacks(self._handler(), False)
        p = xml.parsers.expat.ParserCreate(namespace_separator=' ')
        #expat_handler = expat_reader(self._handler(), asyncio_based_handler=False)
        #p = xml.parsers.expat.ParserCreate(namespace_separator=' ')

        p.StartElementHandler = h.start_element
        p.EndElementHandler = h.end_element
        p.CharacterDataHandler = h.char_data
        p.Parse(source)

        return

