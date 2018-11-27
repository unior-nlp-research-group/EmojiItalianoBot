# -*- coding: utf-8 -*-

import re
import textwrap
import unicodedata

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

# ================================
# AUXILIARY FUNCTIONS
# ================================


def isAlphaAndNotEmoji(uchr):
    import emojiUtil
    return uchr.isalpha() and not uchr in emojiUtil.ALL_EMOJIS

def allAlpha(str):
    unistr = str.decode('utf-8')
    return all(isAlphaAndNotEmoji(uchr) for uchr in unistr)

def containsAlpha(str):
    unistr = str.decode('utf-8')
    return any(isAlphaAndNotEmoji(uchr) for uchr in unistr)

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2)+1):
        yield chr(c)

latin_letters= {}

def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in unicodedata.name(uchr))

def only_roman_chars(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha()) # isalpha suggested by John Machin

def remove_accents_roman_chars(text):
    import string
    text_uni = text.decode('utf-8')
    if not only_roman_chars(text_uni):
        return text
    msg = ''.join(x for x in unicodedata.normalize('NFKD', text_uni) if (x==' ' or x in string.ascii_letters))
    return msg.encode('utf-8')

def normalizeString(text):
    return remove_accents_roman_chars(text.lower()).lower()

def has_roman_chars(text):
    import string
    textNorm = normalizeString(text)
    return any(x in string.ascii_letters for x in textNorm)