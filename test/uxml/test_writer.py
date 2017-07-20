import io
import pytest
from amara3.uxml import writer


def test_raw_basics():
    fp = io.StringIO()
    w = writer.raw(fp)
    w.start_element('spam')
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam>eggs</spam>'


def Xtest_raw_namespacer():
    fp = io.StringIO()
    w = writer.namespacer(fp)
    w.start_element('spam')
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam>eggs</spam>'


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
