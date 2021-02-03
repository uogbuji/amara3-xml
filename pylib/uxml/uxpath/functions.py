# amara3.uxml.uxpath.functions

'''Built-in functions for MicroXPath
'''

__all__ = [
    'BUILTIN_FUNCTIONS',
    ]


#import operator
from functools import wraps
from amara3.uxml.tree import node, element, strval
from .ast import root_node, attribute_node, index_docorder, to_string, to_number, to_boolean

def boolean_arg(ctx, obj):
    '''
    Handles LiteralObjects as well as computable arguments
    '''
    if hasattr(obj, 'compute'):
        obj = next(obj.compute(ctx), False)
    return to_boolean(obj)


def number_arg(ctx, obj):
    '''
    Handles LiteralObjects as well as computable arguments
    '''
    if hasattr(obj, 'compute'):
        obj = next(obj.compute(ctx), False)
    return to_number(obj)


def string_arg(ctx, obj):
    '''
    Handles LiteralObjects as well as computable arguments
    '''
    if hasattr(obj, 'compute'):
        obj = next(obj.compute(ctx), False)
    return to_string(obj)



BUILTIN_FUNCTIONS = {}

def microxpath_function(name):
    def _microxpath_function(f):
        BUILTIN_FUNCTIONS[name] = f
        #global BUILTIN_FUNCTIONS
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return _microxpath_function


@microxpath_function('name')
def name(ctx, obj=None):
    '''
    Yields one string a node name or the empty string, operating on the first item in the provided obj, or the current item if obj is omitted
    If this item is a node, yield its node name (generic identifier), otherwise yield ''
    If obj is provided, but empty, yield ''
    '''
    if obj is None:
        item = ctx.item
    elif hasattr(obj, 'compute'):
        item = next(obj.compute(ctx), None)
    else:
        item = obj
    if isinstance(item, node):
        yield item.xml_name
    else:
        yield ''


@microxpath_function('last')
def last(ctx):
    '''
    '''
    #FIXME: Implement
    yield -1


@microxpath_function('count')
def count(ctx, obj):
    '''
    Yields one number, count of items in the argument sequence
    '''
    yield len(list(obj.compute(ctx)))


@microxpath_function('string')
def string_(ctx, seq=None):
    '''
    Yields one string, derived from the argument literal (or the first item in the argument sequence, unless empty in which case yield '') as follows:

    * If a node, yield its string-value
    * If NaN, yield 'NaN'
    * If +0 or -0, yield '0'
    * If positive infinity, yield 'Infinity'
    * If negative infinity, yield '-Infinity'
    * If an integer, no decimal point and no leading zeros
    * If a non-integer number, at least one digit before the decimal point and at least one digit after
    * If boolean, either 'true' or 'false'
    '''
    if seq is None:
        item = ctx.item
    elif hasattr(seq, 'compute'):
        item = next(seq.compute(ctx), '')
    else:
        item = seq
    yield next(to_string(item), '')


def flatten(iterables):
    return (elem for it in iterables for elem in ([it] if isinstance(it, str) else it))

@microxpath_function('concat')
def concat(ctx, *strings):
    '''
    Yields one string, concatenation of argument strings
    '''
    strings = flatten([ (s.compute(ctx) if callable(s) else s) for s in strings ])
    strings = (next(string_arg(ctx, s), '') for s in strings)
    #assert(all(map(lambda x: isinstance(x, str), strings)))
    #FIXME: Check arg types
    yield ''.join(strings)


@microxpath_function('starts-with')
def starts_with(ctx, full, part):
    '''
    Yields one boolean, whether the first string starts with the second
    '''
    full = next(string_arg(ctx, full), '')
    part = next(string_arg(ctx, part), '')
    yield full.startswith(part)


@microxpath_function('contains')
def contains(ctx, full, part):
    '''
    Yields one boolean, whether the first string contains the second
    '''
    full = next(string_arg(ctx, full), '')
    part = next(string_arg(ctx, part), '')
    yield part in full


@microxpath_function('substring-before')
def substring_before(ctx, full, part):
    '''
    Yields one string
    '''
    full = next(string_arg(ctx, full), '')
    part = next(string_arg(ctx, part), '')
    yield full.partition(part)[0]


@microxpath_function('substring-after')
def substring_after(ctx, full, part):
    '''
    Yields one string
    '''
    full = next(string_arg(ctx, full), '')
    part = next(string_arg(ctx, part), '')
    yield full.partition(part)[-1]


@microxpath_function('substring')
def substring(ctx, full, start, length):
    '''
    Yields one string
    '''
    full = next(string_arg(ctx, full), '')
    start = int(next(to_number(start)))
    length = int(next(to_number(length)))
    yield full[start-1:start-1+length]


@microxpath_function('string-length')
def string_length(ctx, s=None):
    '''
    Yields one number
    '''
    if s is None:
        s = ctx.node
    elif callable(s):
        s = next(s.compute(ctx), '')
    yield len(s)


@microxpath_function('normalize-space')
def normalize_space(ctx, s):
    '''
    Yields one string
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield s


@microxpath_function('translate')
def translate(ctx, s, subst):
    '''
    Yields one string
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield s


@microxpath_function('same-lang')
def same_lang(ctx, seq, lang):
    '''
    Yields one boolean
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield s


@microxpath_function('boolean')
def boolean(ctx, seq):
    '''
    Yields one boolean, false if the argument sequence is empty, otherwise

    * false if the first item is a boolean and false
    * false if the first item is a number and positive or negative zero or NaN
    * false if the first item is a string and ''
    * true in all other cases
    '''
    if hasattr(seq, 'compute'):
        obj = next(seq.compute(ctx), '')
    else:
        obj = seq

    yield next(to_boolean(obj), '')


@microxpath_function('not')
def _not(ctx, obj):
    '''
    Yields one boolean
    '''
    yield not next(boolean_arg(ctx, obj), False)


@microxpath_function('true')
def _true(ctx):
    '''
    Yields one boolean, true
    '''
    yield True


@microxpath_function('false')
def _false(ctx):
    '''
    Yields one boolean, false
    '''
    yield False


@microxpath_function('number')
def number(ctx, seq=None):
    '''
    Yields one float, derived from the first item in the argument sequence (unless empty in which case yield NaN) as follows:

    * If string with optional whitespace followed by an optional minus sign followed by a Number followed by whitespace, converte to the IEEE 754 number that is nearest (according to the IEEE 754 round-to-nearest rule) to the mathematical value represented by the string; in case of any other string yield NaN
    * If boolean true yield 1; if boolean false yield 0
    * If a node convert to string as if by a call to string(); yield the same value as if passed that string argument to number()
    '''
    if hasattr(seq, 'compute'):
        obj = next(seq.compute(ctx), '')
    else:
        obj = seq
    yield next(to_number(obj), '')


@microxpath_function('for-each')
def foreach_(ctx, seq, expr):
    '''
    Yields the result of applying an expression to each item in the input sequence.

    * seq: input sequence
    * expr: expression to be converted to string, then dynamically evaluated for each item on the sequence to produce the result
    '''
    from . import context, parse as uxpathparse

    if hasattr(seq, 'compute'):
        seq = seq.compute(ctx)

    expr = next(string_arg(ctx, expr), '')

    pexpr = uxpathparse(expr)
    for item in seq:
        innerctx = ctx.copy(item=item)
        yield from pexpr.compute(innerctx)


@microxpath_function('lookup')
def lookup_(ctx, tableid, key):
    '''
    Yields a sequence of a single value, the result of looking up a value from the tables provided in the context, or an empty sequence if lookup is unsuccessful

    * tableid: id of the lookup table to use
    * expr: expression to be converted to string, then dynamically evaluated for each item on the sequence to produce the result
    '''
    tableid = next(string_arg(ctx, tableid), '')
    key = next(string_arg(ctx, key), '')
    #value = ctx.
    for item in seq:
        innerctx = ctx.copy(item=item)
        yield from pexpr.compute(innerctx)


@microxpath_function('sum')
def _sum(ctx, seq):
    '''
    Yields one number, the sum, for each item in the argument sequence, of the result of converting as if by a call to number()
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield seq


@microxpath_function('floor')
def _floor(ctx, num):
    '''
    Yields one number, the largest (closest to positive infinity) number that is not greater than the argument and that is an integer.
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield num


@microxpath_function('ceiling')
def _ceiling(ctx, num):
    '''
    Yields one number, the smallest (closest to negative infinity) number that is not less than the argument and that is an integer.
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield num


@microxpath_function('round')
def _round(ctx, num):
    '''
    Yields one number, that which is closest to the argument and that is an integer. If there are two such numbers, then the one that is closest to positive infinity is returned. If the argument is NaN, then NaN is returned. If the argument is positive infinity, then positive infinity is returned. If the argument is negative infinity, then negative infinity is returned. If the argument is positive zero, then positive zero is returned. If the argument is negative zero, then negative zero is returned. If the argument is less than zero, but greater than or equal to -0.5, then negative zero is returned.
    '''
    #FIXME: Implement
    raise NotImplementedError
    yield num

