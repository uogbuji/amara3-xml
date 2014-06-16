# MicroXML parser


Switched to a hand-crafted parser because:

1) Worried about memory consumption of the needed PLY lexer
2) Lack of incremental feed parse for PLY
3) Inspiration from James Clark's JS parser https://github.com/jclark/microxml-js/blob/master/microxml.js

Simple enough to use. Just

>>> from amara3.uxml.parser import parse
>>> d = '<spam>eggs</spam>'
>>> print([e for e in parsefrags(df)])

or for something completely different:

>>> from amara3.uxml.parser import parsefrags
>>> df = iter(('< ', 'spam', '>eggs</spam>',))
>>> print([e for e in parsefrags(df)])

Still very early stages of support/testing

Requires:

* Python 3.4+
* pytest for testing

## Outdated info:

A MicroXML parser for Amara 3.

A lexer for MicroXML for the [PLY](http://www.dabeaz.com/ply/) parser generator on Python 3 (Requires Python 3.3 for fixes to Unicode handling).

Goto http://www.w3.org/community/microxml/ for more about MicroXML.

Install then try:

python3 lib/uxml/lex.py test/uxml/test1.uxml

Uche Ogbuji
uche@ogbuji.net
