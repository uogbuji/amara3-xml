# amara3-xml

A data processing library built on Python 3 and [MicroXML](http://www.w3.org/community/microxml/). This module adds the MicroXML support, and adaptation to classic XML.

[Uche Ogbuji](http://uche.ogbuji.net) < uche@ogbuji.net >
More discussion, etc: https://groups.google.com/forum/#!forum/akara

## Install

Requires:

* Python 3.4+
* [amara3-iri](https://github.com/uogbuji/amara3-iri) package
* [pytest](http://pytest.org/latest/) (for running the test suite)

For the latter 2, you can do:

pip install pytest "amara3-iri>=3.0.0a2"

## Use

Amara in version 3.0 is focused on MicroXML, rather than full XML. However because most of the XML-like data you'll be dealing with is XML 1.0, Amara provides capabilities to parse legacy XML and reduce it to MicroXML. In many cases the biggest implication of this is that namespace information is stripped. As long as you know what you're doing you can get pretty far by ignoring this, but make sure you know what you're doing.

    from amara3.uxml import xml
    
    MONTY_XML = """<monty xmlns="urn:spam:ignored">
      <python spam="eggs">What do you mean "bleh"</python>
      <python ministry="abuse">But I was looking for argument</python>
    </monty>"""

    builder = xml.treebuilder()
    root = builder.parse(MONTY_XML)
    print(root.xml_name) #"monty"
    child = next(root.xml_children)
    print(child) #First text node: "\n  "
    child = next(root.xml_children)
    print(child.xml_value) #"What do you mean \"bleh\""
    print(child.xml_attributes["spam"]) #"eggs"

There are some utilities to make this a bit easier as well.

    from amara3.uxml import xml
    from amara3.uxml.treeutil import *

    MONTY_XML = """<monty xmlns="urn:spam:ignored">
      <python spam="eggs">What do you mean "bleh"</python>
      <python ministry="abuse">But I was looking for argument</python>
    </monty>"""

    builder = xml.treebuilder()
    root = builder.parse(MONTY_XML)
    py1 = next(select_name(root, "python"))
    print(py1.xml_value) #"What do you mean \"bleh\""
    py2 = next(select_attribute(root, "ministry", "abuse"))
    print(py2.xml_value) #"But I was looking for argument"


## Experimental MicroXML parser

For this parser the input truly must be MicroXML. Basics:

	>>> from amara3.uxml.parser import parse
	>>> events = parse('<hello><bold>world</bold></hello>')
	>>> for ev in events: print(ev)
	... 
	(<event.start_element: 1>, 'hello', {}, [])
	(<event.start_element: 1>, 'bold', {}, ['hello'])
	(<event.characters: 3>, 'world')
	(<event.end_element: 2>, 'bold', ['hello'])
	(<event.end_element: 2>, 'hello', [])
	>>> 

Or…And now for something completely different!…Incremental parsing.

	>>> from amara3.uxml.parser import parsefrags
	>>> events = parsefrags(['<hello', '><bold>world</bold></hello>'])
	>>> for ev in events: print(ev)
	... 
	(<event.start_element: 1>, 'hello', {}, [])
	(<event.start_element: 1>, 'bold', {}, ['hello'])
	(<event.characters: 3>, 'world')
	(<event.end_element: 2>, 'bold', ['hello'])
	(<event.end_element: 2>, 'hello', [])
	>>> 

Still very early stages of support/testing

