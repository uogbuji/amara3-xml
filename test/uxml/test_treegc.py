'''
py.test test/uxml/test_treegc.py
'''

import sys
import gc
from asyncio import coroutine

import pytest
from amara3.uxml import tree
from amara3.uxml import treeiter


DOC1 = '<a><b>1</b><b>2</b><b>3</b></a>'
DOC2 = '<a><b>1</b><c>2</c><d>3</d></a>'
DOC3 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>'
DOC4 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'
DOC5 = '<a><b><x>1</x></b><b><x>2</x></b><b><x>3</x></b><b><x>4</x></b></a>'

TREESEQ_CASES = [
    (DOC5, ('a', 'b'), ['1', '2', '3', '4']),
]


@pytest.mark.parametrize('doc,pat,expected', TREESEQ_CASES)
def test_ts_gc(doc, pat, expected):
    @coroutine
    def sink(accumulator):
        old_e = None
        while True:
            e = yield
            #import pprint; pprint.pprint(gc.get_referrers(e))
            #Refs from parent & from frame objects
            assert sys.getrefcount(e) == 6
            #old_e is down to 2 refcounts, 1 from the old_e container & 1 from accumulator
            if old_e is not None: assert sys.getrefcount(old_e) == 2
            accumulator.append(e.xml_value)
            old_e = e
            gc.collect() #Make sure circrefs have been GCed

    values = []
    ts = treeiter.sender(pat, sink(values))
    ts.parse(doc)
    assert values == expected


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
