# Amara 3 MicroXML

Amara 3 is a data processing library built on Python 3 and [MicroXML](http://www.w3.org/community/microxml/). This module adds the MicroXML support, and adaptation to classic XML.

## Parsing MicroXML trees incrementally using patterns

The following code parses a document and builds a tree for each `b` child element of the root `a` element, printing the text content of each of these elements via a coroutine.

	from amara3.uxml import xmliter

	def sink():
	    while True:
	        e = yield
	        print(e.xml_value)

	UXML = '<a><b>1</b><b>2</b><b>3</b></a>'
	ts = xmliter.sender(('a', 'b'), sink())
	ts.parse(UXML)

The printed output is 1 then 2 then 3.

# Contact

[Uche Ogbuji](http://uche.ogbuji.net) < uche@ogbuji.net >

Issues and discussion on [GitHub](https://github.com/uogbuji/amara3-xml)
