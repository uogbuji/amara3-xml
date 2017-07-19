# -----------------------------------------------------------------------------
# amara3.uxml.tree
#
# Basic tree implementation for MicroXML
#
# -----------------------------------------------------------------------------

#See also: http://www.w3.org/community/microxml/wiki/MicroLarkApi

import weakref
from asyncio import coroutine

from amara3.uxml.parser import parse, parser, parsefrags, event

#NO_PARENT = object()


class node(object):
    def __init__(self, parent=None):
        self._xml_parent = weakref.ref(parent) if parent is not None else None
        #self._xml_parent = weakref.ref(parent or NO_PARENT)

    @property
    def xml_parent(self):
        return self._xml_parent() if self._xml_parent else None
        #p = self._xml_parent()
        #return None if p is NO_PARENT else p

    def xml_encode(self):
        raise NotImplementedError

    def xml_write(self, fp):
        fp.write(self.xml_encode())


class element(node):
    '''
    Note: Meant to be bare bones & Pythonic. Does no integrity checking of direct manipulations, such as adding an integer to xml_children, or '1' as an attribute name
    '''
    def __init__(self, name, attrs=None, parent=None):#, ancestors=None):
        self.xml_name = name
        self.xml_attributes = attrs or {}
        self.xml_children = []
        node.__init__(self, parent)
        return

    def xml_encode(self, indent=None, depth=0):
        strbits = ['<', self.xml_name]
        for aname, aval in self.xml_attributes.items():
            strbits.extend([' ', aname, '="', aval, '"'])
        strbits.append('>')
        if indent:
            strbits.append('\n')
            strbits.append(indent*depth)
        for child in self.xml_children:
            if isinstance(child, element):
                strbits.append(child.xml_encode(indent=indent, depth=depth+1))
                if indent:
                    strbits.append('\n')
                    strbits.append(indent*depth)
            else:
                strbits.append(child)
        strbits.extend(['</', self.xml_name, '>'])
        return ''.join(strbits)

    @property
    def xml_value(self):
        '''
        '''
        return ''.join(map(lambda x: x.xml_value, self.xml_children))

    #Really just an alias that forbids specifying position
    def xml_append(self, child):
        '''
        Append a node as the last child

        child - the child to append. If a string, convert to a text node, for convenience
        '''
        self.xml_insert(child)
        return

    def xml_insert(self, child, index=-1):
        '''
        Append a node as the last child

        child - the child to append. If a string, convert to a text node, for convenience
        '''
        if isinstance(child, str):
            child = text(child, parent=self)
        else:
            child._xml_parent = weakref.ref(self)
        if index == -1:
            self.xml_children.append(child)
        else:
            self.xml_children.insert(index, child)
        return

    def __repr__(self):
        return u'{{uxml.element ({0}) "{1}" with {2} children}}'.format(hash(self), self.xml_name, len(self.xml_children))

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'

class text(node, str):
    def __new__(cls, value, parent=None):
        self = super(text, cls).__new__(cls, value)
        return self

    def __init__(self, value, parent=None):#, ancestors=None):
        node.__init__(self, parent)
        return

    def __repr__(self):
        return u'{{uxml.text "{}"...}}'.format(str(self)[:10])

    def xml_encode(self, indent=None, depth=0):
        return str(self)

    @property
    def xml_value(self):
        return str(self)

    @property
    def xml_children(self):
        return []

    @property
    def xml_name(self):
        return '#text'

    #def unparse(self):
    #    return '<' + self.name.encode('utf-8') + unparse_attrmap(self.attrmap) + '>'


def strval(node, outermost=True):
    '''
    XPath-like string value of node
    '''
    if not isinstance(node, element):
        return node.xml_value if outermost else [node.xml_value]
    accumulator = []
    for child in node.xml_children:
        if isinstance(child, text):
            accumulator.append(child.xml_value)
        elif isinstance(child, element):
            accumulator.extend(strval(child, outermost=False))
    if outermost: accumulator = ''.join(accumulator)
    return accumulator


class treebuilder(object):
    def __init__(self):
        self._root = None
        self._parent = None

    @coroutine
    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                new_element = element(ev[1], ev[2], self._parent)
                #Note: not using weakrefs here because these refs are not circular
                if self._parent: self._parent.xml_children.append(new_element)
                self._parent = new_element
                #Hold a reference to the top element of the subtree being built,
                #or it will be garbage collected as the builder moves down the tree
                if not self._root: self._root = new_element
            elif ev[0] == event.characters:
                new_text = text(ev[1], self._parent)
                if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                if self._parent:
                    self._parent = self._parent.xml_parent
        return

    def parse(self, doc):
        #reset
        self._root = None
        self._parent = None
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return self._root


def name_test(name):
    def _name_test(ev):
        return ev[0] == event.start_element and ev[1] == name
    return _name_test


def elem_test():
    def _elem_test(ev):
        return ev[0] == event.start_element
    return _elem_test


MATCHED_STATE = object()


class treesequence(object):
    '''
    #tb = tree.treebuilder()
    >>> from amara3.uxml import tree
    >>> from asyncio import coroutine
    >>> @coroutine
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ...
    >>> values = []
    >>> ts = tree.treesequence(('a', 'b'), sink(values))
    >>> ts.parse('<a><b>1</b><b>2</b><b>3</b></a>')
    >>> values
    ['1', '2', '3']
    '''
    def __init__(self, pattern, sink):
        self._root = None
        self._parent = None
        self._pattern = pattern
        self._states = None
        self._evstack = []
        self._building_depth = 0
        self._sink = sink
        next(sink) #Prime the coroutine
        self._current = None
        self._prep_pattern()

    def _only_name(self, next, name):
        def _only_name_func(ev):
            if ev[0] == event.start_element and ev[1] == name:
                return next
        return _only_name_func

    def _any_name(self, next):
        def _any_name_func(ev):
            if ev[0] == event.start_element:
                return next
        return _any_name_func

    def _any_until(self, next):
        def _any_until_func(ev):
            if ev[0] == event.start_element:
                next_next = next(ev)
                if next_next is not None:
                    return next_next
            return _any_until_func
        return _any_until_func

    def _any(self, next, funcs):
        def _any_func(ev):
            if any( (func(ev) for func in funcs) ):
                return next
        return _any_func

    def _prep_pattern(self):
        next_state = MATCHED_STATE
        for i in range(len(self._pattern)):
            stage = self._pattern[-i-1]
            if isinstance(stage, str):
                if stage == '*':
                    next_state = self._any_name(next_state)
                elif stage == '**':
                    next_state = self._any_until(next_state)
                else:
                    next_state = self._only_name(next_state, stage)
            elif isinstance(stage, tuple):
                new_tuple = tuple(( name_test(substage) if isinstance(substage, str) else substage for substage in stage ))
                next_state = self._any(next_state, new_tuple)
            else:
                raise ValueError('Cannot interpret pattern component {0}'.format(repr(stage)))
        self._states = next_state
        return

    def _match_state(self):
        new_state = self._states
        for depth, ev in enumerate(self._evstack):
            new_state = new_state(ev)
            if new_state == MATCHED_STATE:
                return True
            elif new_state is None:
                return False
        return False

    @coroutine
    def _handler(self):
        while True:
            ev = yield
            if ev[0] == event.start_element:
                self._evstack.append(ev)
                #Keep track of the depth while we're building elements. When we ge back to 0 depth, we're done for this subtree
                if self._building_depth:
                    self._building_depth += 1
                elif self._match_state():
                    self._building_depth = 1
                if self._building_depth:
                    new_element = element(ev[1], ev[2], self._parent)
                    #if self._parent: self._parent().xml_children.append(weakref.ref(new_element))
                    #Note: not using weakrefs here because these refs are not circular
                    if self._parent: self._parent.xml_children.append(new_element)
                    self._parent = new_element
                    #Hold a reference to the top element of the subtree being built,
                    #or it will be garbage collected as the builder moves down the tree
                    if self._building_depth == 1: self._root = new_element
            elif ev[0] == event.characters:
                if self._building_depth:
                    new_text = text(ev[1], self._parent)
                    if self._parent: self._parent.xml_children.append(new_text)
            elif ev[0] == event.end_element:
                self._evstack.pop()
                if self._building_depth:
                    self._building_depth -= 1
                    #Done with this subtree
                    if not self._building_depth:
                        self._sink.send(self._parent)
                    #Pop back up in element ancestry
                    if self._parent:
                        self._parent = self._parent.xml_parent

            #print(ev, self._building_depth, self._evstack)
        return

    def parse(self, doc):
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True)) #Wrap it up
        return


def parse(doc):
    return treebuilder().parse(doc)
