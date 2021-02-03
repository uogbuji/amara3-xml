# amara3.uxml.uxpath.ast

'''Abstract Syntax Tree for parsed MicroXPath.

Heavy debt to: https://github.com/emory-libraries/eulxml/blob/master/eulxml/xpath/ast.py
'''

#Q=a; python -c "from amara3.uxml import tree; tb = tree.treebuilder(); root = tb.parse('<a><b i=\"1.1\"><x>1</x></b><c i=\"1.2\"><x>2</x><d><x>3</x></d></c><x>4</x><y>5</y></a>'); from amara3.uxml.uxpath import context, parse as uxpathparse; ctx = context(root); parsed_expr = uxpathparse('$Q'); result = parsed_expr.compute(ctx); print(list(result))"

__all__ = [
    'serialize',
    'UnaryExpression',
    'BinaryExpression',
    'PredicatedExpression',
    'AbsolutePath',
    'Step',
    'NameTest',
    'NodeTypeTest',
    'AbbreviatedStep',
    'VariableReference',
    'FunctionCall',
    ]


import operator
import functools
from collections.abc import Iterable
from amara3.uxml.tree import node, element, strval
from amara3.uxml.treeutil import descendants


class root_node(node):
    _cache = {}

    def __init__(self, docelem):
        self.xml_name = ''
        self.xml_value = ''
        self.xml_children = [docelem]
        node.__init__(self)

    def __repr__(self):
        return u'{uxpath.rootnode}'

    @staticmethod
    #@functools.lru_cache()
    def get(elem):
        if elem in root_node._cache: return root_node._cache[elem]
        if isinstance(elem, root_node): return elem
        assert isinstance(elem, element), 'Cannot get root node from object {} of type {}'.format(elem, type(elem))
        curr_elem = elem
        parent = curr_elem.xml_parent
        while parent:
            curr_elem = parent
            parent = curr_elem.xml_parent
            if parent in root_node._cache: return root_node._cache[parent]
        return root_node._cache.setdefault(elem, root_node(curr_elem))


class attribute_node(node):
    def __init__(self, name, value, parent):
        self.xml_name = name
        self.xml_value = value
        node.__init__(self, parent)

    def __repr__(self):
        return '{{uxpath.attribute {0}="{1}"}}'.format(self.xml_name, self.xml_value)

    def xml_encode(self):
        return '{{{0}="{1}"}}'.format(self.xml_name, self.xml_value)

    def xml_write(self):
        raise NotImplementedError



def index_docorder(node):
    #Always start at the root
    while node.xml_parent:
        node = node.xml_parent
    index = 0
    node._docorder = index
    for node in descendants(node):
        index += 1
        node._docorder = index


#Casts
def to_string(obj):
    '''
    Cast an arbitrary object or sequence to a string type
    '''
    if isinstance(obj, LiteralWrapper):
        val = obj.obj
    elif isinstance(obj, Iterable) and not isinstance(obj, str):
        val = next(obj, None)
    else:
        val = obj
    if val is None:
        yield ''
    elif isinstance(val, str):
        yield val
    elif isinstance(val, node):
        yield strval(val)
    elif isinstance(val, int) or isinstance(val, float):
        yield str(val)
    elif isinstance(item, bool):
        yield 'true' if item else 'false'
    else:
        raise RuntimeError('Unknown type for string conversion: {}'.format(val))


def to_number(obj):
    '''
    Cast an arbitrary object or sequence to a number type
    '''
    if isinstance(obj, LiteralWrapper):
        val = obj.obj
    elif isinstance(obj, Iterable) and not isinstance(obj, str):
        val = next(obj, None)
    else:
        val = obj
    if val is None:
        #FIXME: Should be NaN, not 0
        yield 0
    elif isinstance(val, str):
        yield float(val)
    elif isinstance(val, node):
        yield float(strval(val))
    elif isinstance(val, int) or isinstance(val, float):
        yield val
    else:
        raise RuntimeError('Unknown type for number conversion: {}'.format(val))


def to_boolean(obj):
    '''
    Cast an arbitrary sequence to a boolean type
    '''
    #if hasattr(obj, '__iter__'):
    if isinstance(obj, LiteralWrapper):
        val = obj.obj
    elif isinstance(obj, Iterable) and not isinstance(obj, str):
        val = next(obj, None)
    else:
        val = obj
    if val is None:
        yield False
    elif isinstance(val, bool):
        yield val
    elif isinstance(val, str):
        yield bool(val)
    elif isinstance(val, node):
        yield True
    elif isinstance(val, float) or isinstance(val, int):
        yield bool(val)
    else:
        raise RuntimeError('Unknown type for boolean conversion: {}'.format(val))


class LiteralWrapper(object):
    '''
    Literal string or number
    '''
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return '{{{}}}'.format(self.__class__.__name__, self.obj)

    def _serialize(self):
        yield(str(self.obj))

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        #self.op is always '-'
        yield self.obj


class UnaryExpression(object):
    '''A unary XPath expression. Really only used with unary minus (self.op == '-')'''

    def __init__(self, op, right):
        assert op == '-'
        self.op = op
        '''the operator used in the expression'''
        self.right = right
        '''the expression the operator is applied to'''

    def __repr__(self):
        return '{{{} {} {}}}'.format(self.__class__.__name__, self.op, serialize(self))

    def _serialize(self):
        yield(self.op)
        for tok in _serialize(self.right):
            yield(tok)

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        #self.op is always '-'
        yield -(to_number(next(self.right.compute(ctx), None)))


BE_KEYWORDS = set(['or', 'and', 'div', 'mod'])
class BinaryExpression(object):
    '''Binary XPath expression, e.g. a/b; a and b; a | b.'''

    def __init__(self, left, op, right):
        self.left = left
        '''the left side of the binary expression'''
        self.op = op
        '''the operator of the binary expression'''
        self.right = right
        '''the right side of the binary expression'''

    def __repr__(self):
        return '{{{} {} {} {}}}'.format(self.__class__.__name__, serialize(self.left), self.op, serialize(self.right))

    def _serialize(self):
        for tok in _serialize(self.left):
            yield(tok)

        if self.op in BE_KEYWORDS:
            yield(' ')
            yield(self.op)
            yield(' ')
        else:
            yield(self.op)

        for tok in _serialize(self.right):
            yield(tok)

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        #print('BINARYEXPRESSION', (self.left, self.op, self.right))
        if self.op == '/':
            #left & right are steps
            selected = self.left.compute(ctx)
            for item in selected:
                new_ctx = ctx.copy(item=item)
                yield from self.right.compute(new_ctx)
        elif self.op == '//':
            #left & right are steps
            #Rewrite the axis to expand the abbreviation
            #Really only needed the first time.
            self.right.axis = 'descendant-or-self'
            selected = self.left.compute(ctx)
            for item in selected:
                new_ctx = ctx.copy(item=item)
                yield from self.right.compute(new_ctx)
        elif self.op == '|':
            #Union expressions require an indexing by doc order
            if not hasattr(ctx.item, '_docorder'):
                index_docorder(ctx.item)
            #XXX Might be more efficient to maintain a list in doc order as left & right are added
            selected = list(self.left.compute(ctx))
            selected.extend(list(self.right.compute(ctx)))
            selected.sort(key=operator.attrgetter('_docorder'))
            yield from selected

        # FIXME: A lot of work to do on comparisons
        elif self.op == '=':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            # print(ctx.item, list(self.left.compute(ctx)), list(self.right.compute(ctx)))
            # If LHS is a node sequence, check comparison on each item
            for i in lhs:
                for j in rhs:
                    i = i.xml_value if isinstance(i, node) else i
                    j = i.xml_value if isinstance(j, node) else j
                    if i == j:
                        yield True
                        return
            yield False
        elif self.op == '!=':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) != next(rhs)
        elif self.op == '>':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) > next(rhs)
        elif self.op == '<':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) < next(rhs)
        elif self.op == '>=':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) >= next(rhs)
        elif self.op == '<=':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) <= next(rhs)
        elif self.op == 'or':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            yield next(lhs) or next(rhs)
        elif self.op == 'and':
            lhs = self.left.compute(ctx)
            rhs = self.right.compute(ctx)
            #lhs_val = next(lhs, None)
            #rhs_val = next(rhs, None)
            #print((self.left, lhs_val, self.right, rhs_val))
            #yield lhs_val and rhs_val
            yield next(lhs) and next(rhs)
        else:
            raise NotImplementedErr('Oops! Operator "{}" not yet implemented'.format(self.op))
        return


class AbsolutePath(object):
    '''
    Absolute XPath path. /a/b/c; //a/ancestor:b/@c
    '''
    def __init__(self, op='/', relative=None):
        #Operator used to root the expression
        self.op = op
        #Relative path after the absolute root operator
        self.relative = relative

    def __repr__(self):
        if self.relative:
            return '{{{} {} {}}}'.format(self.__class__.__name__, self.op, serialize(self.relative))
        else:
            return '{{{} {}}}'.format(self.__class__.__name__, self.op)

    def _serialize(self):
        yield(self.op)
        for tok in _serialize(self.relative):
            yield(tok)

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        rnode = root_node.get(ctx.item)
        if self.relative:
            new_ctx = ctx.copy(item=rnode)
            yield from self.relative.compute(new_ctx)
        else:
            yield rnode


class Step(object):
    '''
    Single step in a relative path. a; @b; text(); parent::foo:bar[5]
    '''
    def __init__(self, axis, node_test):
        self.axis = axis or 'child'
        #NameTest or NodeType object used to select from nodes in the axis
        self.node_test = node_test

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        if self.axis == 'attribute':
            yield('@')
        elif self.axis:
            yield self.axis
            yield('::')

        for tok in self.node_test._serialize():
            yield(tok)

    def compute(self, ctx):
        #print('STEP', (self.axis, self.node_test, ctx.item))
        if self.axis == 'self':
            yield from self.node_test.compute(ctx)
        elif self.axis == 'child':
            for child in ctx.item.xml_children:
                new_ctx = ctx.copy(item=child)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'attribute':
            if isinstance(ctx.item, element):
                for k, v in ctx.item.xml_attributes.items():
                    if self.node_test.name in ('*', k):
                        yield attribute_node(k, v, ctx.item)
        elif self.axis == 'ancestor':
            parent = ctx.item.xml_parent
            while parent:
                new_ctx = ctx.copy(item=parent)
                yield from self.node_test.compute(new_ctx)
                parent = parent.xml_parent
            yield root_node.get(ctx.item)
        elif self.axis == 'ancestor-or-self':
            yield from self.node_test.compute(ctx)
            parent = ctx.item.xml_parent
            while parent:
                new_ctx = ctx.copy(item=parent)
                yield from self.node_test.compute(new_ctx)
            yield root_node.get(parent)
        elif self.axis == 'descendant':
            to_process = list(ctx.item.xml_children)
            while to_process:
                child = to_process[0]
                to_process = list(child.xml_children) + to_process[1:]
                new_ctx = ctx.copy(item=child)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'descendant-or-self':
            yield from self.node_test.compute(ctx)
            to_process = list(ctx.item.xml_children)
            while to_process:
                child = to_process[0]
                to_process = list(child.xml_children) + to_process[1:]
                new_ctx = ctx.copy(item=child)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'following':
            if not ctx.item.xml_parent: return
            start = ctx.item.xml_parent.xml_children.index(ctx.item) + 1
            to_process = list(ctx.item.xml_parent.xml_children)[start:]
            while to_process:
                ff = to_process[0]
                to_process = list(ff.xml_children) + to_process[1:]
                new_ctx = ctx.copy(item=ff)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'following-sibling':
            if not ctx.item.xml_parent: return
            start = ctx.item.xml_parent.xml_children.index(ctx.item) + 1
            for ff in list(ctx.item.xml_parent.xml_children)[start:]:
                new_ctx = ctx.copy(item=ff)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'parent':
            if ctx.item.xml_parent:
                new_ctx = ctx.copy(item=ctx.item.xml_parent)
                yield from self.node_test.compute(new_ctx)
            else:
                yield root_node.get(ctx.item)
        elif self.axis == 'preceding':
            if not ctx.item.xml_parent: return
            start = ctx.item.xml_parent.xml_children.index(ctx.item)
            if start == -1: return
            to_process = list(ctx.item.xml_parent.xml_children)[start:].reverse()
            while to_process:
                prev = to_process[0]
                to_process = to_process[1:] + list(prev.xml_children).reverse()
                new_ctx = ctx.copy(item=prev)
                yield from self.node_test.compute(new_ctx)
        elif self.axis == 'preceding-sibling':
            if not ctx.item.xml_parent: return
            start = ctx.item.xml_parent.xml_children.index(ctx.item)
            if start == -1: return
            to_process = list(ctx.item.xml_parent.xml_children)[:start]
            to_process.reverse()
            for prev in to_process:
                new_ctx = ctx.copy(item=prev)
                yield from self.node_test.compute(new_ctx)
        return

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)


class PredicatedExpression(object):
    '''
    Expression modified by one or more predicates. (1, 2, 3, 4, 5)[. > 3]; parent::foo:bar[5]
    '''
    def __init__(self, lhs, predicates):
        self.lhs = lhs
        #list of predicates filtering the LHS's results
        self.predicates = predicates

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        for tok in _serialize(self.lhs):
            yield(tok)

        for predicate in self.predicates:
            yield('[')
            for tok in _serialize(predicate):
                yield(tok)
            yield(']')

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        #print('PREDICATEDEXPRESSION', (self.lhs, self.predicates))
        for pos, item in enumerate(self.lhs.compute(ctx)):
            #XPath is 1-indexed
            new_ctx = ctx.copy(item=item, pos=pos+1)
            for pred in self.predicates:
                if hasattr(pred, 'compute'):
                    predval = next(pred.compute(new_ctx), False)
                else:
                    predval = pred
                #bools are ints in Python
                if (isinstance(predval, float) or isinstance(predval, int)) and not isinstance(predval, bool):
                    if pos + 1 != int(predval):
                        break
                else:
                    if not next(to_boolean(predval)):
                    #if not next(to_boolean(predval, scalar=True)):
                        break
            else:
                #All predicates true
                yield(item)


class NameTest(object):
    '''
    Element name node test for a Step.
    '''
    def __init__(self, name):
        #XML name or '*'
        self.name = name

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield(self.name)

    def __str__(self):
        return ''.join(self._serialize())

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        #print('NAMETEST', (self.name, ctx.item))
        if self.name == '*':
            yield ctx.item
        else:
            #yield from (n for n in nodeseq if n.xml_name == self.name)
            if isinstance(ctx.item, element) and ctx.item.xml_name == self.name:
                yield ctx.item


class NodeTypeTest(object):
    '''
    Node type node test for a Step.
    '''
    def __init__(self, name):
        #node type name, 'node' or 'text'
        self.name = name

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield(self.name)
        yield('(')
        yield(')')

    def __str__(self):
        return ''.join(self._serialize())

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        if (self.name == 'node' and isinstance(ctx.item, node)) \
            or isinstance(ctx.item, str):
            yield ctx.item


class AbbreviatedStep(object):
    '''
    Abbreviated XPath step. '.' or '..'
    '''
    def __init__(self, abbr):
        #abbreviated step
        self.abbr = abbr

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield(self.abbr)

    def compute(self, ctx):
        #print('ABBREVIATEDSTEP', (self.abbr))
        if self.abbr == '.':
            yield ctx.item
        elif self.abbr == '..':
            #parent axis
            #assert isinstance(ctx.item, node)
            if ctx.item.xml_parent:
                yield ctx.item.xml_parent
            else:
                yield root_node.get(ctx.item)

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)


class VariableReference(object):
    '''
    XPath variable reference, e.g. '$foo'
    '''
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield('$')
        yield(self.name)

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        yield ctx.variables[self.name]


class FunctionCall(object):
    '''
    XPath function call, e.g. 'foo()'; 'foo(1, 'a', $var)'
    '''
    def __init__(self, name, args):
        self.name = name
        #list of argument expressions
        self.args = args

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield(self.name)
        yield('(')
        if self.args:
            for tok in _serialize(self.args[0]):
                yield(tok)

            for arg in self.args[1:]:
                yield(',')
                for tok in _serialize(arg):
                    yield(tok)
        yield(')')

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        if not self.name in ctx.functions:
            #FIXME: g11n
            raise RuntimeError('Unknown function: {}'.format(self.name))
        func = ctx.functions[self.name]
        yield from func(ctx, *self.args)


class Sequence(object):
    '''
    MicroXPath sequence, e.g. '()'; '(1, 'a', $var)'
    '''
    def __init__(self, items):
        #list of argument expressions
        self.items = items

    def __repr__(self):
        return '{{{} {}}}'.format(self.__class__.__name__, serialize(self))

    def _serialize(self):
        yield('(')
        if self.items:
            for tok in _serialize(self.items[0]):
                yield(tok)

            for item in self.items[1:]:
                yield(',')
                for tok in _serialize(item):
                    yield(tok)
        yield(')')

    def __call__(self, ctx):
        '''
        Alias for user convenience
        '''
        yield from self.compute(ctx)

    def compute(self, ctx):
        for item in self.items:
            if hasattr(item, 'compute'):# and iscallable(item.compute):
                yield from item.compute(ctx)
            else:
                yield item


def serialize(xp_ast):
    '''Serialize an XPath AST as a valid XPath expression.'''
    return ''.join(_serialize(xp_ast))


def _serialize(xp_ast):
    '''Generate token strings which, when joined together, form a valid
    XPath serialization of the AST.'''

    if hasattr(xp_ast, '_serialize'):
        for tok in xp_ast._serialize():
            yield(tok)
    elif isinstance(xp_ast, str):
        yield(repr(xp_ast))
