import itertools
from amara3.uxml.tree import treebuilder, element
from amara3.util import coroutine

doc = '<a>1<aa a="1">2<aaa>3</aaa>4<aab>5</aab>6</aa>7<ab a="2">8</ab></a>'
tb = treebuilder()
root = tb.parse(doc)

def descendants(elem):
    for child in elem.xml_children:
        yield child
        if isinstance(child, element):
            yield from descendants(child)

print('descendants')

for e in descendants(root):
    print (e)

def select_elements(source):
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: isinstance(x, element), source)


def select_name(source, name):
    return filter(lambda x: x.xml_name == name, select_elements(source))


def select_name_pattern(source, pat):
    return filter(lambda x: pat.match(x.xml_name) is not None, select_elements(source))


print('select_name')

for e in select_name(descendants(root), 'aaa'):
    print (e)

print('select_name_pattern')

import re
HAS_B_PAT = re.compile('.*b.*')

for e in select_name_pattern(descendants(root), HAS_B_PAT):
    print (e)


def select_value(source, val):
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: x.xml_value == val, source)

print('select_value')

for e in select_value(descendants(root), '3'):
    print (e)


def select_attribute(source, name, val=None):
    def check(x):
        if val is None:
            return name in x.xml_attributes
        else:
            return name in x.xml_attributes and x.xml_attributes[name] == val
    return filter(check, select_elements(source))
    
print('select_attribute 1')

for e in select_attribute(descendants(root), 'a'): print (e)

print('select_attribute 2')

for e in select_attribute(descendants(root), 'a', '1'): print (e)


def following_siblings(e):
    it = itertools.dropwhile(lambda x: x != e, e.xml_parent.xml_children)
    next(it) #Skip the element itself
    return it

print('following_siblings')

for e in following_siblings(next(select_name(descendants(root), 'aa'))): print (e)


print('etc.')

print (root.xml_value)

for e in itertools.takewhile(
            lambda x: x.xml_name != 'aaa',
            filter(
                lambda x: isinstance(x, element),
                descendants(root)
                )
            ):
    print (e)

