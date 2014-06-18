#Sample usage, from project root dir:
#python example/markdownlinkchecker.py README.md

import sys
import markdown #pip install markdown

from amara3.uxml.parser import parse, event

with open(sys.argv[1]) as f:
    h = markdown.markdown(f.read(), safe_mode='escape', output_format='html5')

#Needs a proper document element
h = '<html>' + h + '</html>'
#print(h)

for ev in parse(h):
    if ev[0] == event.start_element:
        if ev[1] == 'a':
            attrs = ev[2]
            print(attrs['href'])

