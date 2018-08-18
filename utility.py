# -*- coding: utf-8 -*-

import re
import textwrap

def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def representsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

re_digits = re.compile('^\d+$')

def hasOnlyDigits(s):
    return re_digits.match(s) != None

def representsIntBetween(s, low, high):
    if not representsInt(s):
        return False
    sInt = int(s)
    if sInt>=low and sInt<=high:
        return True
    return False

def representsFloatBetween(s, low, high):
    if not representsFloat(s):
        return False
    sFloat = float(s)
    if sFloat>=low and sFloat<=high:
        return True
    return False

def makeArray2D(data_list, length=2):
    return [data_list[i:i+length] for i in range(0, len(data_list), length)]


def distributeElementMaxSize(seq, maxSize=5):
    lines = len(seq) / maxSize
    if len(seq) % maxSize > 0:
        lines += 1
    avg = len(seq) / float(lines)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def escapeMarkdown(text):
    for char in '*_`[':
        text = text.replace(char, '\\'+char)
    return text

def unindent(s):
    return re.sub('[ ]+', ' ', textwrap.dedent(s))

#####

def isAlphaAndNotEmoji(uchr):
    import emojiUtil
    return uchr.isalpha() and not uchr in emojiUtil.ALL_EMOJIS

def allAlpha(str):
    unistr = str.decode('utf-8')
    return all(isAlphaAndNotEmoji(uchr) for uchr in unistr)

def containsAlpha(str):
    unistr = str.decode('utf-8')
    return any(isAlphaAndNotEmoji(uchr) for uchr in unistr)
