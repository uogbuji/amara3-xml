# amara3-xml

A data processing library built on Python 3 and [MicroXML](http://www.w3.org/community/microxml/). This module adds the MicroXML support, and adaptation to legacy XML.

[Uche Ogbuji](http://uche.ogbuji.net) < uche@ogbuji.net >
More discussion, etc: https://groups.google.com/forum/#!forum/akara

## Install

Requires:

* Python 3.4+
* [amara3-iri](https://github.com/uogbuji/amara3-iri) package
* [pytest](http://pytest.org/latest/) (for running the test suite)

For the latter 2, you can do:

pip install pytest "amara3-iri<=3.0.0a2"

## Use

Basics.

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

