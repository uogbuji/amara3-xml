#python -m amara3.uxml.uxpathhack

'''
FIXME: WILL SOON BE OBSOLETE AS WE SWITCH TO A MORE LASTING XPATH SOLUTION
'''

from amara3.uxml.treeutil import *
from amara3.uxml.tree import *
#from versa.pipeline import *

#versamaterialize = materialize
#def materialize(typ, rel=None, derive_origin=None, unique=None, links=None, inverse=False, split=None, attributes=None):
#    return versamaterialize(typ, rel, derive_origin, unique, links, inverse, split)


def poormans_xpath(path):
    attr_check = None
    seq = path.split('//')
    seq = list(itertools.chain.from_iterable(zip(seq, (['**']*len(seq)))))[:-1]
    seq = [ seg.split('/') for seg in seq ]
    seq = list(itertools.chain.from_iterable(seq))
    if seq and seq[-1].startswith('@'):
        attr_check = seq[-1][1:]
        seq = seq[:-1]
    return seq, attr_check


'''

'''

def xpath(pathstr):
    '''
    Versa pipeline action function generator to obtain a value from XPath


    '''
    #FIXME Use instead amara3.uxml.uxpath
    parsedpath, attr_check = poormans_xpath(pathstr)
    def _xpath(ctx):
        xmltreenode = ctx.extras['xmltreenode']
        #FIXME: Handle multiple nodes
        if parsedpath:
            result = next(select_pattern(xmltreenode, parsedpath), None)
        else:
            #Must be an attribute query
            result = xmltreenode
        if attr_check:
            return result.xml_attributes.get(attr_check, '')
        else:
            return strval(result) if result else ''
    return _xpath


def strval(elem, accumulator=None, outermost=True):
    '''
    XPath-like string value of element
    '''
    accumulator = accumulator or []
    for child in elem.xml_children:
        if isinstance(child, text):
            accumulator.append(child.xml_value)
        elif isinstance(child, element):
            accumulator.extend(strval(child, accumulator=accumulator, outermost=False))
    if outermost: accumulator = ''.join(accumulator)
    return accumulator
