#amara3.uxml

import xml.parsers.expat
from amara3.uxml import tree

# 3 handler functions

p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

p.Parse("""<?xml version="1.0"?>
<parent id="top"><child1 name="paul">Text goes here</child1>
<child2 name="fred">More text</child2>
</parent>""", 1)

def xmlconvert(source):
    '''
    Convert XML 1.0 to MicroXML
    source - XML 1.0 input

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



    return uxml, extras

