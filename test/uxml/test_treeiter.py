import pytest #Consider also installing pytest_capturelog
from amara3.uxml import treeiter


DOC1 = '<a><b>1</b><b>2</b><b>3</b></a>'
DOC2 = '<a><b>1</b><c>2</c><d>3</d></a>'
DOC3 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x></a>'
DOC4 = '<a><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'

def test_ts_basics():
    def sink(accumulator):
        while True:
            e = yield
            accumulator.append(e.xml_value)

    values = []
    ts = treeiter.sender(('a', 'b'), sink(values))
    ts.parse(DOC1)
    assert values == ['1', '2', '3']

    values = []
    ts = treeiter.sender(('a', '*'), sink(values))
    ts.parse(DOC1)
    assert values == ['1', '2', '3']

    values = []
    ts = treeiter.sender(('a', ('b', 'c')), sink(values))
    ts.parse(DOC2)
    assert values == ['1', '2']

    values = []
    ts = treeiter.sender(('a', '**', 'x'), sink(values))
    ts.parse(DOC3)
    assert values == ['1', '2', '3', '4']

    values = []
    ts = treeiter.sender(('*', '**', 'x'), sink(values))
    ts.parse(DOC3)
    assert values == ['1', '2', '3', '4']

    values = []
    ts = treeiter.sender(('a', '**', 'x'), sink(values))
    ts.parse(DOC4)
    assert values == ['1', '2', '3', '4']

    values = []
    ts = treeiter.sender(('*', '**', 'x'), sink(values))
    ts.parse(DOC4)
    assert values == ['1', '2', '3', '4']

    values = []
    ts = treeiter.sender(('*', '*'), sink(values))
    ts.parse(DOC3)
    assert values == ['1', '23', '4']

    return


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
