#Sample usage, from project root dir:
#python example/markdownlinkchecker.py README.md

import sys
from collections import deque

from amara3.uxml.parser import parsefrags, event

docfragments = deque()

with open(sys.argv[1]) as f:
    for line in f.readlines():
        docfragments.append(line)


for ev in parsefrags(docfragments):
    print (ev)


from amara3.util import coroutine
from amara3.uxml.parser import parser, event

@coroutine
def handler():
    while True:
        ev = yield
        print(ev)
    return

h = handler()
p = parser(h)

p.send(('<hello id', False))
p.send(('="12"', False))
p.send(('>', False))
p.send(('world', False))
p.send(('</hello>', True))
