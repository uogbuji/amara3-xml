# amara3.uxml.uxpath.functions

'''Built-in functions for MicroXPath
'''

__all__ = [
    'BUILTIN_FUNCTIONS',
    ]


#import operator
from functools import wraps
from amara3.uxml.tree import node, element
from .ast import root_node, attribute_node, index_docorder, strval, to_number, to_boolean

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


@microxpath_function('last')
def last(ctx):
    '''
    '''
    #FIXME: Implement
    yield -1


@microxpath_function('count')
def count(ctx, seq):
    '''
    Yields one number, count of items in the argument sequence
    '''
    yield len(list(seq.compute(ctx)))


@microxpath_function('string')
def string_(ctx, seq=None):
    '''
    Yields one string, derived from the first item in the argument sequence (unless empty in which case yield '') as follows:

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
        item = ctx.node
    else:
        item = next(seq.compute(ctx), '')
    if isinstance(item, str):
        yield item
    elif isinstance(item, node):
        yield strval(item)
    elif isinstance(item, int) or isinstance(item, float):
        yield str(item)
    elif isinstance(item, bool):
        yield 'true' if item else 'false'
    else:
        #FIXME: Warning about unknown object?
        yield ''


def flatten(iterables):
    return (elem for it in iterables for elem in ([it] if isinstance(it, str) else it))

@microxpath_function('concat')
def concat(ctx, *strings):
    '''
    Yields one string, concatenation of argument strings
    '''
    strings = flatten([ (s.compute(ctx) if callable(s) else s) for s in strings ])
    #assert(all(map(lambda x: isinstance(x, str), strings)))
    #FIXME: Check arg types
    yield ''.join(strings)


@microxpath_function('starts-with')
def starts_with(ctx, full, part):
    '''
    Yields one boolean, whether the first string starts with the second
    '''
    #FIXME: Check arg types
    yield full.startswith(part)


@microxpath_function('contains')
def contains(ctx, full, part):
    '''
    Yields one boolean, whether the first string contains the second
    '''
    #FIXME: Check arg types
    yield part in full


@microxpath_function('substring-before')
def substring_before(ctx, full, part):
    '''
    Yields one string
    '''
    yield full.partition(part)[0]


@microxpath_function('substring-after')
def substring_after(ctx, full, part):
    '''
    Yields one string
    '''
    yield full.partition(part)[-1]


@microxpath_function('substring')
def substring(ctx, full, start, length):
    '''
    Yields one string
    '''
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
    raise NotImplementedErr
    yield s


@microxpath_function('translate')
def translate(ctx, s, subst):
    '''
    Yields one string
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield s


@microxpath_function('same-lang')
def same_lang(ctx, seq, lang):
    '''
    Yields one boolean
    '''
    #FIXME: Implement
    raise NotImplementedErr
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
    item = next(seq.compute(ctx), false)
    if isinstance(item, bool):
        yield item
    elif isinstance(item, str) and item == '':
        yield false
    elif (isinstance(item, int) or isinstance(item, float)) and item == 0:
        yield false
    else:
        yield true


@microxpath_function('not')
def _not(ctx, seq):
    '''
    Yields one boolean
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield seq


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
    if seq is None:
        item = ctx.node
    else:
        item = next(seq.compute(ctx), '')
    if isinstance(item, str):
        yield item
    elif isinstance(item, node):
        yield strval(item)
    elif isinstance(item, int) or isinstance(item, float):
        yield str(item)
    elif isinstance(item, bool):
        yield 'true' if item else 'false'
    else:
        #FIXME: Warning about unknown object?
        yield ''


@microxpath_function('sum')
def _sum(ctx, seq):
    '''
    Yields one number, the sum, for each item in the argument sequence, of the result of converting as if by a call to number()
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield seq


@microxpath_function('floor')
def _floor(ctx, num):
    '''
    Yields one number, the largest (closest to positive infinity) number that is not greater than the argument and that is an integer.
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield num


@microxpath_function('ceiling')
def _sum(ctx, num):
    '''
    Yields one number, the smallest (closest to negative infinity) number that is not less than the argument and that is an integer.
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield num


@microxpath_function('round')
def _sum(ctx, num):
    '''
    Yields one number, that which is closest to the argument and that is an integer. If there are two such numbers, then the one that is closest to positive infinity is returned. If the argument is NaN, then NaN is returned. If the argument is positive infinity, then positive infinity is returned. If the argument is negative infinity, then negative infinity is returned. If the argument is positive zero, then positive zero is returned. If the argument is negative zero, then negative zero is returned. If the argument is less than zero, but greater than or equal to -0.5, then negative zero is returned.
    '''
    #FIXME: Implement
    raise NotImplementedErr
    yield num
