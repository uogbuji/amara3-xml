#amara3.uxml.parser

'''
Hand-crafted parser for MicroXML, with much owing to James Clark's Javascript work at

https://github.com/jclark/microxml-js/blob/master/microxml.js
'''

import re

#states
PRE_ELEMENT = 1
IN_ELEMENT = 2
PRE_TAG_GI = 3
PRE_COMPLETE_TAG_GI = 4
TAG_GI = 5
COMPLETE_TAG = 6
COMPLETE_DOC = 7

#Events
START_ELEMENT = 1
END_ELEMENT = 2
CHARACTERS = 3

BOM = '\uFEFF'

CHARACTER = re.compile('[\u0009\u000a\u0020-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]')

#MicroXML production [7] Basically CHARACTER - [\u0026\u003C\u003E]
DATACHAR = re.compile('[\u0009\u000a\u0020-\u0025\u0027-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]')

NAMESTARTCHAR = re.compile('[A-Za-z_\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D' \
            '\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF' \
            '\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]')

NAMECHAR =  re.compile('[0-9A-Za-z_\u00B7-\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u037D' \
            '\u037F-\u1FFF\u200C-\u200D\u203F-\u2040\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF' \
            '\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]')

#For single quoted attrs
ATTRIBVALCHAR_SGL = '[\u0020-\u0025\u0028-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

#For double quoted attrs
ATTRIBVALCHAR_DBL = '[\u0020-\u0021\\\u0023-\u0025\u0027-\u003B\u003D\u003F-\u007e\u00a0-\ud7ff\ue000-\ufdcf\ufdf0-\ufffd' \
            '\U00010000-\U0001fffd\U00020000-\U0002fffd\U00030000-\U0003fffd\U00040000-\U0004fffd\U00050000-\U0005fffd\U00060000-\U0006fffd' \
            '\U00070000-\U0007fffd\U00080000-\U0008fffd\U00090000-\U0009fffd\U000a0000-\U000afffd\U000b0000-\U000bfffd\U000c0000-\U000cfffd' \
            '\U000d0000-\U000dfffd\U000e0000-\U000efffd\U000f0000-\U000ffffd\U00100000-\U0010fffd]'

# Tokens

WS = '[\u0009\u000A\u0020]'

def coroutine(func):
    '''
    A simple tool to eliminate the need to call next() to kick-start a co-routine
    From David Beazley: http://www.dabeaz.com/generators/index.html
    '''
    def start(*args,**kwargs):
        coro = func(*args,**kwargs)
        next(coro)
        return coro
    return start


@coroutine
def parser(handler, strict=True):
    #abspos = 0
    line_count = 1
    col_count = 1
    window = ''
    pos = 0
    wlen = 0
    backtrack = 0
    state = PRE_ELEMENT
    done = False
    element_stack = []
    try:
        try:
            while not done:
                #import pdb; pdb.set_trace()
                frag, done = yield
                #print(frag, done)
                if not frag: continue #Ignore empty additions
                window += frag
                wlen += len(frag)
                #FIXME: throw away unneeded, prior bits of window here
                need_input = False
                while not need_input:
                    if state == PRE_ELEMENT:
                        #Eat up any whitespace
                        try:
                            while window[pos] in ' \r\n\t':
                                pos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                        if window[pos] == '<':
                            pos += 1
                            state = PRE_TAG_GI
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                    if state in (PRE_TAG_GI, PRE_COMPLETE_TAG_GI):
                        pending_event = START_ELEMENT if state == PRE_TAG_GI else END_ELEMENT
                        #import pdb; pdb.set_trace()
                        #Eat up any whitespace
                        try:
                            while window[pos] in ' \r\n\t':
                                pos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        if state == PRE_TAG_GI and window[pos] == '/':
                            pos += 1
                            state = PRE_COMPLETE_TAG_GI
                            pending_event = END_ELEMENT
                            continue
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                        advpos = pos
                        try:
                            if NAMESTARTCHAR.match(window[advpos]):
                                advpos += 1
                                while NAMECHAR.match(window[advpos]):
                                    advpos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        else:
                            gi = window[pos:advpos]
                            pos = advpos
                            state = COMPLETE_TAG
                    if state == COMPLETE_TAG:
                        #Eat up any whitespace
                        try:
                            while window[pos] in ' \r\n\t':
                                pos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                        if window[pos] == '>':
                            pos += 1
                            #FIXME: check whether state is end of single root element
                            state = IN_ELEMENT
                            if pending_event == START_ELEMENT:
                                handler.send((pending_event, gi, {}, element_stack))
                                element_stack.append(gi)
                            else:
                                opened = element_stack.pop()
                                if opened != gi:
                                    raise RuntimeError('Expected close element {0}, found {1}'.format(opened, gi))
                                handler.send((pending_event, gi, element_stack))
                                if not element_stack: #and if strict
                                    state = COMPLETE_DOC
                            if pos == wlen:
                                if done:
                                    #Error: unfinished business if this is opening tag
                                    break
                                else:
                                    need_input = True
                                    continue
                    if state == IN_ELEMENT:
                        advpos = pos
                        try:
                            while DATACHAR.match(window[advpos]):
                                advpos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        else:
                            chars = window[pos:advpos]
                            pos = advpos
                            handler.send((CHARACTERS, chars))
                        if window[pos] == '<':
                            pos += 1
                        advpos = pos
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                        state = PRE_TAG_GI
                    if state == COMPLETE_DOC:
                        if pos == wlen:
                            break #All done!
                        #Eat up any whitespace
                        try:
                            while window[pos] in ' \r\n\t':
                                pos += 1
                        except IndexError:
                            if not done: need_input = True #Do not advance until we have enough input
                            continue
                        #if not done and pos == wlen:
                        #    need_input = True
                        #    continue
                        if pos == wlen:
                            break
                        else:
                            raise RuntimeError('Junk after document element')
                    #print('END1')
                #print('END2')
            sentinel = yield #Avoid StopIteration in parent from running off enf of coroutine?
        except GeneratorExit:
            #close() called
            pass #Any cleanup
    except StopIteration:
        pass #Any cleanup
    return

'''
echo "from amara3.uxml.parser import parsefrags" > /tmp/spam.py
echo "for e in parsefrags(('<spa', 'm>eggs</spam>')): print(e)" >> /tmp/spam.py
python -m pdb -c "b /Users/uche/.local/venv/py3/lib/python3.3/site-packages/amara3/uxml/parser.py:96" /tmp/spam.py
'''

@coroutine
def handler(accumulator):
    while True:
        event = yield
        accumulator.append(event)
    return


def parse(text):
    acc = []
    h = handler(acc)
    p = parser(h)
    p.send((text, True))
    p.close()
    h.close()
    for event in acc:
        yield event


def parsefrags(textfrags):
    acc = []
    h = handler(acc)
    p = parser(h)
    #fragcount = len(textfrags)
    for i, frag in enumerate(textfrags):
        p.send((frag, False))
    p.send(('', True)) #Wrap it up
    p.close()
    h.close()
    for event in acc:
        yield event
