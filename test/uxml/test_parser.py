import pytest
from asyncio import coroutine

from amara3.uxml.parser import parse, parser, parsefrags, event


TEST_PATTERN1 = []

DOC1_FRAGS = ([
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
],
[(event.start_element, 'spam', {}, []), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

#Append a version fo the doc chopped up  fed in character by character
DOC1_FRAGS[0].append([ c for c in DOC1_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC1_FRAGS)

DOC2_FRAGS = ([
    ('<spam x=\'y\'>eggs</spam>',),
],
[(event.start_element, 'spam', {'x': 'y'}, []), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

DOC2_FRAGS[0].append([ c for c in DOC2_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC2_FRAGS)

DOC3_FRAGS = ([
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
],
[(event.start_element, 'spam', {}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, 'b'), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

DOC3_FRAGS[0].append([ c for c in DOC3_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC3_FRAGS)

DOC4_FRAGS = ([
    ('<spam x=\'y\' zz=\'zzz\'><a>b</a>eggs</spam>',),
],
[(event.start_element, 'spam', {'x': 'y', 'zz': 'zzz'}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, 'b'), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

DOC4_FRAGS[0].append([ c for c in DOC4_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC4_FRAGS)

DOC5_FRAGS = ([
    ('<spam x=\'&lt;y&#x3E;\' zz=\'zzz\'><a>b</a>eggs</spam>',),
],
[(event.start_element, 'spam', {'x': '<y>', 'zz': 'zzz'}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, 'b'), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

DOC5_FRAGS[0].append([ c for c in DOC5_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC5_FRAGS)

DOC6_FRAGS = ([
    ('<spam x=\'&lt;y&#x3E;\' zz=\'zzz\'><a> &lt;boo!&#x3E; </a>eggs</spam>',),
],
[(event.start_element, 'spam', {'x': '<y>', 'zz': 'zzz'}, []), (event.start_element, 'a', {}, ['spam']), (event.characters, ' <boo!> '), (event.end_element, 'a', ['spam']), (event.characters, 'eggs'), (event.end_element, 'spam', [])])

DOC6_FRAGS[0].append([ c for c in DOC6_FRAGS[0][0] ])

TEST_PATTERN1.append(DOC6_FRAGS)


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


#def test_basic():

@coroutine
def handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return

alldocfrags = [ doc for (df, ev) in TEST_PATTERN1 for doc in df ]
allexpectedev = [ ev for (df, ev) in TEST_PATTERN1 for doc in df ]

@pytest.mark.parametrize('docfrag,events', zip(alldocfrags, allexpectedev))
def test_feed_frags1(docfrag, events):
    acc = []
    h = handler(acc)
    p = parser(h)
    lendoc = len(docfrag)
    for i, frag in enumerate(docfrag):
        #print(i, frag)
        p.send((frag, i == lendoc - 1))
    p.close()
    h.close()
    assert acc == events
