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


def test_raw_quote_attr1():
    fp = io.StringIO()
    w = writer.raw(fp)
    w.start_element('spam', attribs={'a': '"', 'b': '&'})
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam a=\'"\' b="&amp;">eggs</spam>'


def test_raw_quote_attr2():
    fp = io.StringIO()
    w = writer.raw(fp)
    w.start_element('spam', attribs={'a': "'"})
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam a="\'">eggs</spam>'


def test_ns_quote_attr1():
    fp = io.StringIO()
    w = writer.namespacer(fp, prefixes={'': 'http://example.com'})
    w.start_element('spam', attribs={'a': '"', 'b': '&'})
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam xmlns="http://example.com" a=\'"\' b="&amp;">eggs</spam>'


def test_ns_quote_attr2():
    fp = io.StringIO()
    w = writer.namespacer(fp, prefixes={'': 'http://example.com'})
    w.start_element('spam', attribs={'a': "'"})
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam xmlns="http://example.com" a="\'">eggs</spam>'


def Xtest_raw_namespacer():
    fp = io.StringIO()
    w = writer.namespacer(fp)
    w.start_element('spam')
    w.text('eggs')
    w.end_element('spam')
    assert fp.getvalue() == '<spam>eggs</spam>'


if __name__ == '__main__':
    raise SystemExit("Run with py.test")
