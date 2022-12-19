# MicroXPath implementation (amara3)

[Uche Ogbuji](http://uche.ogbuji.net) < uche@ogbuji.net >

## Quick start

(For non-Python folks)

* Install [Python 3.5+ or later](https://www.python.org/downloads/)
* Download the [amara3-xml](https://pypi.python.org/pypi/amara3-xml) package and install (`python setup.py install`)

(For Python folks, you should be using pip: `pip install amara3-xml`)

## Basic use

Using the parser for XML (not MicroXML). Namespaces will be ignored and so will some other XML lexical quirks.

    from amara3.uxml.tree import parse
    from amara3.uxml.uxpath import context, parse as uxp
    
    CHANSON_XML = """<TEI>
      <teiHeader>
        <title>Chanson Balisage</title>
      </teiHeader>
      <text>
        <lg type="poem">
        <l><ref target="#a1" type="noteAnchor">Bar ‘Ebroyo</ref> cursed CSS, he cursed</l>
        <l>And cursed XForms, he smote his XML</l>
        </lg>
        <note id="a1" type="footnote"><bibl>
          <author>Nathan P. Gibson</author>, <author>Winona Salesky</author> &amp; <author>David A. Michelson</author>, <title>Encoding Western and Non-Western Names for Ancient Syriac Authors</title>, Balisage, 2015</bibl>
        </note>
      </text>
    </TEI>"""
    
    SMALL_DOC = '<doc>text</doc>'
    
    VARS = {'n': 1, 't': 'a', 'd': SMALL_DOC}
    
    root = parse(CHANSON_XML)
    ctx = context(root, variables=VARS)
    
    #Sequence of all authors in the footnote
    path = uxp('TEI/text/note//author')
    for item in path(ctx):
        #Print the element back out as MicroXML
        print(item.xml_encode())
    
    print('--- %< --->')
    
    #Sequence of the first two authors
    path = uxp('(TEI/text/note//author[1], TEI/text/note//author[2])')
    for item in path(ctx):
        #Print the element back out as MicroXML
        print(item.xml_encode())
        
    #Tally of authors in the footnote
    path = uxp('count(TEI/text/note//author)')
    print(next(path(ctx)))


$var[1]; (a or b)[foo][@bar]