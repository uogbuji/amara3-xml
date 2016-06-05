# -*- coding: utf-8 -*-
from distutils.core import setup, Extension
import sys, os

versionfile = 'lib/version.py'
exec(compile(open(versionfile, "rb").read(), versionfile, 'exec'), globals(), locals())
__version__ = '.'.join(version_info)

#here = os.path.abspath(os.path.dirname(__file__))

#v = open(os.path.join(here, 'lib', '__init__.py'))
#version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
#v.close()

#try:
#    README = open(os.path.join(here, 'README.txt')).read()
#    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
#except IOError:
#    README = CHANGES = ''

LONGDESC = '''amara3-xml
==========

A data processing library built on Python 3 and `MicroXML`_. This module
adds the MicroXML support, and adaptation to classic XML.

`Uche Ogbuji`_ < uche@ogbuji.net > More discussion, etc:
https://groups.google.com/forum/#!forum/akara

Install
-------

Requires:

-  Python 3.4+
-  `amara3-iri`_ package
-  `pytest`_ (for running the test suite)

For the latter 2, you can do:

pip install pytest “amara3-iri>=3.0.0a2”

Use
---

Amara in version 3.0 is focused on MicroXML, rather than full XML.
However because most of the XML-like data you’ll be dealing with is XML
1.0, Amara provides capabilities to parse legacy XML and reduce it to
MicroXML. In many cases the biggest implication of this is that
namespace information is stripped. As long as you know what you’re doing
you can get pretty far by ignoring this, but make sure you know what
you’re doing.

::

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

::

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

Experimental MicroXML parser
----------------------------

For this parser the input truly must be MicroXML. Basics:

::

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

::

    >>> from amara3.uxml.parser import parsefrags
    >>> events = parsefrags(['<hello', '><bold>world</bold></hello>'])
    >>> for ev in events: print(ev)
    ...
    (<event.start_element: 1>, 'hello', {}, [])
    (<event.start_element: 1>, 'bold', {}, ['hello'])
    (<event.characters: 3>, 'world')
    (<event.end_element: 2>, 'bold

.. _MicroXML: http://www.w3.org/community/microxml/
.. _Uche Ogbuji: http://uche.ogbuji.net
.. _amara3-iri: https://github.com/uogbuji/amara3-iri
.. _pytest: http://pytest.org/latest/
'''

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError) as e:
    #long_description = open('README.md').read()
    long_description = LONGDESC

#If you run into a prob with missing limits.h on Ubuntu/Mint, try:
#sudo apt-get install libc6-dev
cxmlstring = Extension('amara3.cmodules.cxmlstring', sources=['lib/cmodules/xmlstring.c'])

setup(
    name='amara3-xml',
    version=__version__,
    #version='3.0.0a4patch2',
    description="Amara3 project, which offers a variety of data processing tools. This module adds the MicroXML support, and adaptation to classic XML.",
    #long_description=README + '\n\n' +  CHANGES,
    author='Uche Ogbuji',
    author_email='uche@ogbuji.net',
    #url='http://uche.ogbuji.net',
    url = 'https://github.com/uogbuji/amara3-xml',
    download_url = 'https://github.com/uogbuji/amara3-xml/tarball/v' + __version__,
    license='Apache',
    package_dir={'amara3': 'lib'},
    packages = ['amara3', 'amara3.uxml', 'amara3.uxml.uxpath'],
    keywords = ["xml", "web", "data"],
    #scripts=['exec/exhibit_agg', 'exec/exhibit_lint'],
    classifiers = [ # From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        #"Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    long_description = long_description,
    ext_modules = [cxmlstring]
    #install_requires=[
      # -*- Extra requirements: -*-
    #    'pytest',
    #    'sphinx'
    #],
)
