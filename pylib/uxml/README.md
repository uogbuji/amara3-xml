# MicroXML parser


Switched to a hand-crafted parser because:

1) Worried about memory consumption of the needed PLY lexer
2) Lack of incremental feed parse for PLY
3) Inspiration from James Clark's JS parser https://github.com/jclark/microxml-js/blob/master/microxml.js

Uche Ogbuji
uche@ogbuji.net

## Install

Requires:

* Python 3.4+
* amara3-iri package
* pytest (for running the test suite)

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

More discussion, etc: https://groups.google.com/forum/#!forum/akara


# Outdated info:

A MicroXML parser for Amara 3.

A lexer for MicroXML for the [PLY](http://www.dabeaz.com/ply/) parser generator on Python 3 (Requires Python 3.3 for fixes to Unicode handling).

Goto http://www.w3.org/community/microxml/ for more about MicroXML.

Install then try:

python3 lib/uxml/lex.py test/uxml/test1.uxml
