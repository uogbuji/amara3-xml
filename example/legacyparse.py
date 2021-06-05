'''
Not sure what this file was all about. WIll delete soon
'''

from amara3.uxml.xml import parse, buffer_handler
evs = []
h = buffer_handler(evs)
parse('<?xml version="1.0"?><root xmlns="http://default-namespace.org/" xmlns:py="http://www.python.org/ns/" spam="eggs" py:spam1="eggs+"><py:elem1/><elem2 xmlns=""/></root>', h)
print(evs)


def handle_start_element(ev):
    pass

