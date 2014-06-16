import pytest


DOC1_FRAGS = [
    ('<spam>eggs</spam>',),
    (' <spam>eggs</spam> ',),
    ('  <spam>eggs</spam>  ',),
    ('<', 'spam>eggs</spam>',),
    #('<', 'spam>eggs</spam>',),
    ('< ', 'spam', '>eggs</spam>',),
    ('< ', 'spam', '>', 'eggs</spam>',),
    ('< ', 'spam', '>eggs', '</spam>',),
    ('< ', 'spam', '>eggs', '<', '/spam>',),
    ('< ', 'spam', '>eggs', '<', '/', 'spam>',),
    ('< ', 'spam', '>eggs', '<', '/', 'spam', '>',),
    ('<s', 'pam>eggs</spam>',),
    ('<spa', 'm>eggs</spam>',),
    ('<spam', '>eggs</spam>',),
]

DOC1_FRAGS.append([ c for c in DOC1_FRAGS[0] ])

DOC2_FRAGS = [
    ('<spam x=\'y\'>eggs</spam>',),
]

DOC2_FRAGS.append([ c for c in DOC2_FRAGS[0] ])

DOC3_FRAGS = [
    ('<spam><a>b</a>eggs</spam>',),
    ('<spam><a>b</a', '>eggs</spam>',),
    ('<spam>', '<a>b</a>eggs<', '/spam>',),
    ('<spam>', '<a>b</a>eggs</spam>',),
    ('<spam><a>', 'b</a>eggs</spam>',),
    ('<spam><a>', 'b</a', '>eggs</spam>',),
    ('<spam><a>b<', '/a>eggs</spam>',),
    ('<spam><a>b<', '/a>eggs</spam>',),
    ('<spam><a>b</a>', 'eggs</spam>',),
    ('<spam><a>b</a>', 'eggs</sp', 'am>',),
    ('<sp', 'am><a>b</a>', 'eggs</spam>',),
    ('<', 'spam', '><a>b</a>eggs', '<', '/spam>',),
    ('<', 'sp', 'am', '><a>b</a>eggs', '<', '/spam>',),
    ('<sp', 'am><a>b</a>eggs', '<', '/spam>',),
    ('< ', 'spam ', ' ><a>b</a>eggs', '<', ' / spam > ',),
]

DOC3_FRAGS.append([ c for c in DOC3_FRAGS[0] ])

DOC4_FRAGS = [
    ('<spam x=\'y\' zz=\'zzz\'><a>b</a>eggs</spam>',),
]

DOC4_FRAGS.append([ c for c in DOC4_FRAGS[0] ])

INCOMPLETE_DOC1 = [
    ('<spam>',),
    (' <spam> ',),
    ('  <spam>  ',),
    ('<', 'spam>',),
    ('< ', 'spam>',),
    ('<s', 'pam>',),
    ('<spa', 'm>',),
    ('<spam', '>',),
]


from amara3.uxml.parser import parse, parser, event
from amara3.uxml.parser import coroutine

#def test_basic():

@coroutine
def handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return


@pytest.mark.parametrize('docfrag', DOC1_FRAGS)
def test_feed_frags1(docfrag):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == [(event.start_element, 'spam', {}, []), (event.characters, 'eggs'), (event.end_element, 'spam', [])]

@pytest.mark.parametrize('docfrag', DOC2_FRAGS)
def test_feed_frags2(docfrag):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == [(event.start_element, 'spam', {'x': 'y'}, []), (event.characters, 'eggs'), (event.end_element, 'spam', [])]

@pytest.mark.parametrize('docfrag', DOC3_FRAGS)
def test_feed_frags3(docfrag):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == [(event.start_element, 'spam', {}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, 'b'), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])]

@pytest.mark.parametrize('docfrag', DOC4_FRAGS)
def test_feed_frags4(docfrag):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == [(event.start_element, 'spam', {'x': 'y', 'zz': 'zzz'}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, 'b'), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])]

    #raise Exception(repr(docfrag))

