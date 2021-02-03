# pytest test/uxml/test_chunk_parse_write.py

import io
import os
import pytest
from amara3.uxml import xmliter, xml
from amara3.uxml import writer


def test_quoteattr1(testresourcepath):
    def record_sink(writer_obj):
        while True:
            rec = yield
            writer.write(rec, writer_obj)

    fp = io.StringIO()
    w = writer.namespacer(fp, prefixes={'': 'http://example.com'})
    w.start_element('wrapper')
    ts = xmliter.sender(('wrapper', 'record'), record_sink(w))
    ts.parse_file(open(os.path.join(testresourcepath, 'quoteattr.xml'), 'rb'))
    w.end_element('wrapper')
    assert fp.getvalue() == '''\
<wrapper xmlns="http://example.com">\
<record test='"' id="1&amp;1" lang="en">One</record>\
<record test="'" id="2&amp;2" lang="en">Two</record>\
</wrapper>\
'''


if __name__ == '__main__':
    raise SystemExit("Run with py.test")

#@coroutine
