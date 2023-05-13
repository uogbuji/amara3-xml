# amara3.uxml
'''
Parse an input source with MicroXML (or full XML) into an Amara 3 tree

>>> from amara3.uxml import parse
>>> top = parse('<a><b i="1.1">+2+</b></a>')

Warning: if you pass a string, make sure it's a byte string,
not a Unicode object. You might also want to wrap it with
amara.lib.inputsource.text if it's not obviously XML
(to avoid e.g. its getting confused for a file name)
'''

from amara3.uxml import tree

TB = tree.treebuilder()
parse = TB.parse


try:
    import amara3.cmodules.cxmlstring
    isxml = amara3.cmodules.cxmlstring.isxml
except ImportError:
    pass

