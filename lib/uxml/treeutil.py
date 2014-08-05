import itertools
from amara3.uxml.tree import element

def descendants(elem):
    for child in elem.xml_children:
        yield child
        if isinstance(child, element):
            yield from descendants(child)

def select_elements(source):
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: isinstance(x, element), source)


def select_name(source, name):
    return filter(lambda x: x.xml_name == name, select_elements(source))


def select_name_pattern(source, pat):
    return filter(lambda x: pat.match(x.xml_name) is not None, select_elements(source))


def select_value(source, val):
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: x.xml_value == val, source)

def select_attribute(source, name, val=None):
    def check(x):
        if val is None:
            return name in x.xml_attributes
        else:
            return name in x.xml_attributes and x.xml_attributes[name] == val
    return filter(check, select_elements(source))

def following_siblings(e):
    it = itertools.dropwhile(lambda x: x != e, e.xml_parent.xml_children)
    next(it) #Skip the element itself
    return it

