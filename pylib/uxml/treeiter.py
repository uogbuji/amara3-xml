# -----------------------------------------------------------------------------
# amara3.uxml.treeiter
#
# Iterator (generator and coroutine) facilities for MicroXML tree objects
#
# -----------------------------------------------------------------------------

import asyncio
import collections

from .parser import parser, parsefrags, event
from .tree import element, text, name_test


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
    def __init__(self, patterns, sinks, prime_sinks=True):
        '''
        Initializer

        Params:
            patterns - pattern or list of patterns for subtrees to be generated,
                each a tuple of element names, or the special wildcards '*' or '**'
                '*' matches any single element. '**' matches any nestign of elements to arbitrary depth.
                Resulting subtrees are sent to the corrersponding sink coroutine,
                so number of patterns must match number of sinks
            sinks - coroutine to be sent element subtrees as generated from parse.
                Each coroutine receives subtrees based on the corrersponding pattern,
                so number of patterns must match number of sinks
            prime_sinks - if True call next() on each coroutine to get it started
        '''
        self._patterns = [patterns] if isinstance(patterns, tuple) and isinstance(patterns[0], str) else patterns
        self._pattern_count = len(self._patterns)
        self._sinks = sinks if isinstance(sinks, list) or isinstance(sinks, tuple) else [sinks]
        if len(self._sinks) != self._pattern_count:
            raise ValueError('Number of patterns must match number of sinks')
        self._roots = [None] * self._pattern_count
        self._parents = [None] * self._pattern_count
        self._stateses = [None] * self._pattern_count
        self._evstacks = [[]] * self._pattern_count
        self._building_depths = [0] * self._pattern_count
        #if asyncio.iscoroutine(sink):
        if prime_sinks:
            for sink in self._sinks:
                if isinstance(sink, collections.Iterable):
                    next(sink)  # Prime coroutine
        self._currents = [None] * self._pattern_count
        self._prep_patterns()

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

    def _prep_patterns(self):
        next_state = MATCHED_STATE
        for ix, pattern in enumerate(self._patterns):
            for i in range(len(pattern)):
                stage = pattern[-i-1]
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
            self._stateses[ix] = next_state
        return

    def _match_state(self, ix):
        new_state = self._stateses[ix]
        for depth, ev in enumerate(self._evstacks[ix]):
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
            for ix, evstack in enumerate(self._evstacks):
                building_depth = self._building_depths[ix]
                parent = self._parents[ix]
                if ev[0] == event.start_element:
                    evstack.append(ev)
                    #Keep track of the depth while we're building elements. When we ge back to 0 depth, we're done for this subtree
                    if building_depth:
                        building_depth += 1
                        self._building_depths[ix] = building_depth
                    elif self._match_state(ix):
                        building_depth = self._building_depths[ix] = 1
                    if building_depth:
                        new_element = element(ev[1], ev[2], parent)
                        #if parent: parent().xml_children.append(weakref.ref(new_element))
                        #Note: not using weakrefs here because these refs are not circular
                        if parent: parent.xml_children.append(new_element)
                        parent = self._parents[ix] = new_element
                        #Hold a reference to the top element of the subtree being built,
                        #or it will be garbage collected as the builder moves down the tree
                        if building_depth == 1: self._roots[ix] = new_element
                elif ev[0] == event.characters:
                    if building_depth:
                        new_text = text(ev[1], parent)
                        if parent: parent.xml_children.append(new_text)
                elif ev[0] == event.end_element:
                    evstack.pop()
                    if building_depth:
                        building_depth -= 1
                        self._building_depths[ix] = building_depth
                        #Done with this subtree
                        if not building_depth:
                            self._sinks[ix].send(parent)
                        #Pop back up in element ancestry
                        if parent:
                            parent = self._parents[ix] = parent.xml_parent

                #print(ev, building_depth, evstack)
        return

    def parse(self, doc):
        h = self._handler()
        p = parser(h)
        p.send((doc, False))
        p.send(('', True))  # Wrap it up
        return
