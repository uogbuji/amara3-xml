#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Highly recommend installing using `pip install -U .` not `python setup.py install`

Uses pkgutil-style namespace package (Working on figuring out PEP 420)

Note: careful not to conflate install_requires with requirements.txt

https://packaging.python.org/discussions/install-requires-vs-requirements/

Reluctantly use setuptools for now to get install_requires & long_description_content_type

$ python -c "import amara3; import amara3.iri; import amara3.uxml; import amara3.uxml.version; print(amara3.uxml.version.version_info)"
('3', '0', '1')
'''

import sys
from setuptools import setup, Extension
#from distutils.core import setup, Extension
#from distutils.core import Extension

PROJECT_NAME = 'amara3.xml'
PROJECT_DESCRIPTION = 'Amara3 project, which offers a variety of data processing tools. This module adds the MicroXML support, and adaptation to classic XML.'
PROJECT_LICENSE = 'License :: OSI Approved :: Apache Software License'
PROJECT_AUTHOR = 'Uche Ogbuji'
PROJECT_AUTHOR_EMAIL = 'uche@ogbuji.net'
PROJECT_URL = 'https://github.com/uogbuji/amara3-xml'
PACKAGE_DIR = {'amara3': 'pylib'}
PACKAGES = [
    'amara3.uxml',
    'amara3.uxml.uxpath'
]
SCRIPTS = [
    'exec/microx'
]

CORE_REQUIREMENTS = [
    'amara3.iri>=3.0.1',
    'nameparser',
    'pytest',
    'ply',
    'html5lib',
]

# From http://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Development Status :: 4 - Beta",
    #"Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Internet :: WWW/HTTP",
]

KEYWORDS=['xml', 'web', 'data']

version_file = 'pylib/uxml/version.py'
exec(compile(open(version_file, "rb").read(), version_file, 'exec'), globals(), locals())
__version__ = '.'.join(version_info)

#If you run into a prob with missing limits.h on Ubuntu/Mint, try:
#sudo apt-get install libc6-dev
cxmlstring = Extension('amara3.cmodules.cxmlstring', sources=['clib/xmlstring.c'], include_dirs=['clib'])

LONGDESC = '''# Amara 3 XML

Python 3 tools for processing [MicroXML](http://www.w3.org/community/microxml/), a simplification of XML. Amara 3 XML implements the MicroXML data model, and allows you to parse into this from tradiional XML and MicroXML.

The `microx` command line tool is especially useful for quick query and processing of XML.

## Install

Requires Python 3.4+. Just run:

```
pip install amara3.xml
```

## Use

Though Amara 3 is focused on MicroXML rather than full XML, the reality is that
most of the XML-like data you’ll be dealing with is full XML
1.0. his package provides capabilities to parse legacy XML and reduce it to
MicroXML. In many cases the biggest implication of this is that
namespace information is stripped. As long as you know what you’re doing
you can get pretty far by ignoring this, but make sure you know what
you’re doing.

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
    (<event.end_element: 2>, 'bold

## Implementation notes

Switched to a hand-crafted parser because:

1) Worried about memory consumption of the needed PLY lexer
2) Lack of incremental feed parse for PLY
3) Inspiration from James Clark's JS parser https://github.com/jclark/microxml-js/blob/master/microxml.js

----

Author: [Uche Ogbuji](http://uche.ogbuji.net) <uche@ogbuji.net>

'''

LONGDESC_CTYPE = 'text/markdown'

setup(
    #namespace_packages=['amara3'],
    name=PROJECT_NAME,
    version=__version__,
    description=PROJECT_DESCRIPTION,
    license=PROJECT_LICENSE,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_AUTHOR_EMAIL,
    #maintainer=PROJECT_MAINTAINER,
    #maintainer_email=PROJECT_MAINTAINER_EMAIL,
    url=PROJECT_URL,
    package_dir=PACKAGE_DIR,
    packages=PACKAGES,
    scripts=SCRIPTS,
    ext_modules = [cxmlstring],
    install_requires=CORE_REQUIREMENTS,
    classifiers=CLASSIFIERS,
    long_description=LONGDESC,
    long_description_content_type=LONGDESC_CTYPE,
    keywords=KEYWORDS,
)

