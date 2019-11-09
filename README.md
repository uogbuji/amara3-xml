# amara3-xml

[MicroXML](http://www.w3.org/community/microxml/) component of Amara3 project, which contains a variety of data processing tools.

Data processing library built on Python 3 and . This module adds the MicroXML support, and adaptation to classic XML.

[Uche Ogbuji](http://uche.ogbuji.net) < uche@ogbuji.net >
More discussion, etc: https://groups.google.com/forum/#!forum/akara

## Install

Requires Python 3.5+. Use pip

```
pip install amara3-xml
```

## Use

Main focus is MicroXML, rather than full XML. However because most of the XML-like data you'll be dealing with is XML 1.0, Amara provides capabilities to parse legacy XML and reduce it to MicroXML. In many cases the biggest implication of this is that namespace information is stripped. As long as you know what you're doing you can get pretty far by ignoring this, but make sure you know what you're doing.

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

### HTML parsing

You can use Amara to parse HTML

```
from amara3.uxml import html5
import urllib.request
with urllib.request.urlopen('http://uche.ogbuji.net/') as response:
    #Element object for <html> wrapper (no explicit document root object in MicroXML)
    e = html5.parse(response)
```

Warning: html5lib is the underlying parser, so unfortunately Python 3.8 support will be broken until we have an [upstream fix](https://github.com/html5lib/html5lib-python/issues/419).

### Iterated parsed tree objects

Amara supports building trees from XML, but a common problem in doing this is that large XML files turn into tree objects that consume a great deal of memory. Amara provides treeiter parsers from MicroXML, full XML and HTML5 which allow you to specify an element pattern so that the parse only retrieves a subset of the document at a time.

Here is an example parsing from XML

```
from amara3.uxml import xmliter
def sink(accumulator):
    while True:
        e = yield
        accumulator.append(e.xml_value)
    values = []
ts = xmliter.sender(('a', 'b'), sink(values))
ts.parse('<a xmlns="urn:namespaces:suck"><b>1</b><b>2</b><b>3</b></a>')
print(values)
#['1', '2', '3']
```

The logical structure you have to use is a bit awkward, because pyexpat, the underlying parser does not have a coroutine-based API.

### Experimental MicroXML parser

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

