import itertools
from amara3.uxml.tree import element

def descendants(elem):
    '''
    Yields all the elements descendant of elem in document order
    '''
    for child in elem.xml_children:
        yield child
        if isinstance(child, element):
            yield from descendants(child)


def select_elements(source):
    '''
    Yields all the elements from the source
    source - if an element, yields all child elements in order; if any other iterator yields the elements from that iterator
    '''
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: isinstance(x, element), source)


def select_name(source, name):
    '''
    Yields all the elements with the given name
    source - if an element, starts with all child elements in order; can also be any other iterator
    name - will yield only elements with this name
    '''
    return filter(lambda x: x.xml_name == name, select_elements(source))


def select_name_pattern(source, pat):
    '''
    Yields elements from the source whose name matches the given regular expression pattern
    source - if an element, starts with all child elements in order; can also be any other iterator
    pat - re.pattern object
    '''
    return filter(lambda x: pat.match(x.xml_name) is not None, select_elements(source))


def select_value(source, val):
    '''
    Yields elements from the source with the given value (accumulated child text)
    source - if an element, starts with all child elements in order; can also be any other iterator
    val - string value to match
    '''
    if isinstance(source, element):
        source = source.xml_children
    return filter(lambda x: x.xml_value == val, source)


def select_attribute(source, name, val=None):
    '''
    Yields elements from the source having the given attrivute, optionally with the given attribute value
    source - if an element, starts with all child elements in order; can also be any other iterator
    name - attribute name to check
    val - if None check only for the existence of the attribute, otherwise compare the given value as well
    '''
    def check(x):
        if val is None:
            return name in x.xml_attributes
        else:
            return name in x.xml_attributes and x.xml_attributes[name] == val
    return filter(check, select_elements(source))

def following_siblings(elem):
    '''
    Yields elements and text which have the same parent as elem, but come afterward in document order
    '''
    it = itertools.dropwhile(lambda x: x != elem, elem.xml_parent.xml_children)
    next(it) #Skip the element itself
    return it

#

MATCHED_STATE = object()

def name_test(next, name):
    def _name_test(node):
        if isinstance(node, element) and node.xml_name == name:
            return next
    return _name_test

def elem_test(next):
    def _elem_test(node):
        if isinstance(node, element):
            return next
    return _elem_test

def any_until(next):
    def _any_until(node):
        if isinstance(node, element):
            next_next = next(node)
            if next_next is not None:
                return next_next
        return _any_until #Return this same state until we can match the next
    return _any_until

def any_(next, funcs):
    def _any(node):
        if any( (func(node) for func in funcs) ):
            return next
    return _any

def _prep_pattern(pattern):
    next_state = MATCHED_STATE
    #Work from the end of the pattern back to the beginning
    for i in range(len(pattern)):
        stage = pattern[-i-1] #reverse indexing
        if isinstance(stage, str):
            if stage == '*':
                next_state = elem_test(next_state)
            elif stage == '**':
                next_state = any_until(next_state)
            else:
                next_state = name_test(next_state, stage)
        elif isinstance(stage, tuple):
            new_tuple = tuple(( name_test(substage) if isinstance(substage, str) else substage for substage in stage ))
            next_state = any_(next_state, new_tuple)
        else:
            raise ValueError('Cannot interpret pattern component {0}'.format(repr(stage)))
    return next_state


def select_pattern(node, pattern, state=None):
    '''
    Yield descendant nodes matching the given pattern specification
    pattern - tuple of steps, each of which matches an element by name, with "*" acting like a wildcard, descending the tree in tuple order
                sort of like a subset of XPath in Python tuple form
    state - for internal use only
    
    pattern examples:
    
    ("a", "b", "c") - all c elements whose parent is a b element whose parent is an a element whose parent is node
    ("*", "*") - any "grandchild" of node
    ("*", "*", "*") - any "great grandchild" of node
    ("**", "a") - any a descendant of node

    >>> from amara3.uxml import tree
    >>> from amara3.uxml.treeutil import *
    >>> 
    >>> tb = tree.treebuilder()
    >>> DOC = '<a xmlns="urn:namespaces:suck"><b><x>1</x></b><c><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'
    >>> root = tb.parse(DOC)
    >>> results = [ e.xml_value for e in select_pattern(root, ('**', 'x')) ]
    >>> results
    ['1', '2', '3', '4']
    '''
    if state is None:
        state = _prep_pattern(pattern)
    #for child in select_elements(elem):
    if isinstance(node, element):
        for child in node.xml_children:
            new_state = state(child)
            if new_state == MATCHED_STATE:
                yield child
            elif new_state is not None:
                yield from select_pattern(child, None, state=new_state)
    return

