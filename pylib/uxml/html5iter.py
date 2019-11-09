########################################################################
# amara3.uxml.htmliter
"""

"""

from . import tree
from . import treeiter
from .treeutil import *
from . import html5


class sender(treeiter.sender):
    '''
    >>> from amara3.uxml import html5iter
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ...
    >>> values = []
    >>> ts = html5iter.sender(('html', 'body', 'ul', 'li'), sink(values))
    >>> ts.parse('<html><head><title></head><body><ul><li>1</li><li>2</li><li>3</li></ul></body>')
    >>> values
    ['1', '2', '3']
    '''
    def parse(self, doc):
        h = self._handler()
        p = html5.parser(h)
        p.send((doc, False))
        p.send(('', True))  # Wrap it up
        return

