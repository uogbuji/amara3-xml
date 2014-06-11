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


from amara3.uxml.parser import parse, parser, START_ELEMENT, END_ELEMENT, CHARACTERS
from amara3.uxml.parser import coroutine

#def test_basic():

@coroutine
def handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return


@pytest.mark.parametrize('docfrag', DOC1_FRAGS)
def test_feed_frags(docfrag):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == [(START_ELEMENT, 'spam', {}, []), (CHARACTERS, 'eggs'), (END_ELEMENT, 'spam', [])]

    #raise Exception(repr(docfrag))

