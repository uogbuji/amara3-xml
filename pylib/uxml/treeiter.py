# -----------------------------------------------------------------------------
# amara3.uxml.treeiter
#
# Iterator (generator and coroutine) facilities for MicroXML tree objects
#
# -----------------------------------------------------------------------------

import asyncio

from .parser import parser, parsefrags, event
from .tree import element, text


MATCHED_STATE = object()


class sender:
    '''
    Parser object that feeds a coroutine with tree fragments based on an element pattern

    >>> from amara3.uxml import treeiter
    ... def sink(accumulator):
    ...     while True:
    ...         e = yield
    ...         accumulator.append(e.xml_value)
    ...
    >>> values = []
    >>> ts = treeiter.sender(('a', 'b'), sink(values))
    >>> ts.parse('<a><b>1</b><b>2</b><b>3</b></a>')
    >>> values
    ['1', '2', '3']
    '''
    def __init__(self, pattern, sink, prime_sink=True):
        self._root = None
        self._parent = None
        self._pattern = pattern
        self._states = None
        self._evstack = []
        self._building_depth = 0
        self._sink = sink
        #if asyncio.iscoroutine(sink):
        if prime_sink:
            next(sink)  # Prime coroutine
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

    @asyncio.coroutine
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

