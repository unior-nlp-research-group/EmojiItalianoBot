# -*- coding: utf-8 -*-

import logging
import re
import json
import emoji_tables
from emoji_unicode import Emoji
from emoji_unicode.utils import code_point_to_unicode, unicode_to_code_point
from collections import defaultdict
from random import randint

##################
## EMOJI TAGS TABLES
##################

#ALL_EMOJIS_INCLUDED_COMPOSITIONAL = emoji_tables.ALL_EMOJIS
#TO BE UPDATED ONCE A DAY OR SO

with open("EmojiLanguages/_emojiDesc.json") as f:
    EMOJI_TO_DESC_TABLE = {
        key.encode('utf-8'): value.encode('utf-8')
        for key, value in json.load(f).iteritems()
    }

with open("EmojiLanguages/Italian.json") as f:
    EMOJI_TO_TEXT_TABLE_IT = {
        key.encode('utf-8'): [x.encode('utf-8') for x in value]
        for key, value in json.load(f).iteritems()
    }

ALL_EMOJIS = EMOJI_TO_TEXT_TABLE_IT.keys()

with open("EmojiLanguages/English.json") as f:
    EMOJI_TO_TEXT_TABLE_EN = {
        key.encode('utf-8'): [x.encode('utf-8') for x in value]
        for key, value in json.load(f).iteritems()
    }

TEXT_TO_EMOJI_TABLE_IT = defaultdict(lambda: [])
for emoji, tags in EMOJI_TO_TEXT_TABLE_IT.iteritems():
    for t in tags:
        TEXT_TO_EMOJI_TABLE_IT[t.lower()].append(emoji)
        tSplit = t.split(' ')
        if len(tSplit)>1:
            for w in tSplit:
                TEXT_TO_EMOJI_TABLE_IT[w.lower()].append(emoji)

TEXT_TO_EMOJI_TABLE_EN = defaultdict(lambda: [])
for emoji, tags in EMOJI_TO_TEXT_TABLE_EN.iteritems():
    for t in tags:
        TEXT_TO_EMOJI_TABLE_EN[t.lower()].append(emoji)
        tSplit = t.split(' ')
        if len(tSplit) > 1:
            for w in tSplit:
                TEXT_TO_EMOJI_TABLE_EN[w.lower()].append(emoji)

def getDescriptionForEmoji(emoji):
    return EMOJI_TO_DESC_TABLE.get(emoji)

def getTagsForEmoji(emoji, italian=True):
    if italian:
        return EMOJI_TO_TEXT_TABLE_IT.get(emoji)
    return EMOJI_TO_TEXT_TABLE_EN.get(emoji)

def getEmojisForTag(tag, italian=True):
    tagLowerCase = tag.lower()
    if italian:
        return TEXT_TO_EMOJI_TABLE_IT.get(tagLowerCase)
    return TEXT_TO_EMOJI_TABLE_EN.get(tagLowerCase)


def getRandomUnicodeTag(italian=True):
    if italian:
        return TEXT_TO_EMOJI_TABLE_IT.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_IT) - 1)]
    else:
        return TEXT_TO_EMOJI_TABLE_EN.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_EN) - 1)]


def getRandomSingleEmoji(italian=True, escludeStar = True):
    if italian:
        result = EMOJI_TO_TEXT_TABLE_IT.keys()[randint(1, len(EMOJI_TO_TEXT_TABLE_IT) - 1)]
    else:
        result = EMOJI_TO_TEXT_TABLE_EN.keys()[randint(1, len(EMOJI_TO_TEXT_TABLE_EN) - 1)]
    if escludeStar and '*' in result:
        return getRandomSingleEmoji(italian, escludeStar)
    return result

##################
## FUNCTIONS
##################

def getCodePointStr(text):
   return ', '.join(['-'.join([str(hex(ord(c)))[2:] for c in e]) for e in text.decode('utf-8')])

def getCodePointWithInitialZeros(e):
    codePoints = [str(hex(ord(c)))[2:] for c in e.decode('utf-8')]
    codePoints = [x if len(x)>2 else "00" + x for x in codePoints]
    result = '_'.join(codePoints)
    return result

def stringHasOnlyStandardEmojis(text):
    return splitEmojis(text, normalize=False) is not None


def normalizeEmojiText(text_utf):
    parts = splitEmojis(text_utf)
    if parts is None:
        return None
    return ''.join(parts)


# this is the symbol that creates problems most of the times
UNI_EMPTY_SYMBOL = u'\ufe0f'
# key caps #, *, 1-9
KEY_CAP_NUMBEERS = [u'\u0023', u'\u002A',
                    u'\u0030', u'\u0031', u'\u0032', u'\u0033', u'\u0034', u'\u0035',
                    u'\u0036', u'\u0037', u'\u0038', u'\u0039']
KEY_CAP_FRAME = u'\u20E3'


def checkIfValidEmoji(uni_e, normalize):
    if uni_e in emoji_tables.ALL_EMOJIS:
        return uni_e, True
    if normalize and len(uni_e) == 2 :
        if uni_e[1] == UNI_EMPTY_SYMBOL and uni_e[0] in emoji_tables.ALL_EMOJIS:
            return uni_e[0], True
        elif uni_e[0] in KEY_CAP_NUMBEERS and uni_e[1]==KEY_CAP_FRAME:
            return uni_e[0]+UNI_EMPTY_SYMBOL+uni_e[1], True
    return uni_e, False

# returns None if any emoji is not recognized
def splitEmojis(text_utf, normalize=True):
    parts = []
    textuni = text_utf.decode('utf-8')
    s = 0
    e = len(textuni)
    while(True):
        span = textuni[s:e]
        #print "span:{} s:{} e:{}".format([str(hex(ord(c)))[2:] for c in span], s, e)
        span, spanIsValidEmoji = checkIfValidEmoji(span, normalize)
        if spanIsValidEmoji:
            parts.append(span.encode('utf-8'))
            if e == len(textuni):
                return parts
            textuni = textuni[e:]
            s = 0
            e = len(textuni)
        else:
            e -= 1
            if s==e:
                return None

def splitEmojisUni(textuni, normalize=True):
    parts = []
    s = 0
    e = len(textuni)
    while (True):
        span = textuni[s:e]
        # print "span:{} s:{} e:{}".format([str(hex(ord(c)))[2:] for c in span], s, e)
        span, spanIsValidEmoji = checkIfValidEmoji(span, normalize)
        if spanIsValidEmoji:
            parts.append(span)
            if e == len(textuni):
                return parts
            textuni = textuni[e:]
            s = 0
            e = len(textuni)
        else:
            e -= 1
            if s == e:
                return None

def getStringWithoutStandardEmojis(text):
    textuni = text.decode('utf-8')
    return emoji_tables.emoji_pattern.sub('', textuni).encode('utf-8')  # no emoji

def stringContainsAnyStandardEmoji(text):
    return getStringWithoutStandardEmojis(text) != text


'''
def getNormalizedEmojiUni_via_emoji_unicode_lib(text_uni):
    emoji = Emoji(text_uni)
    norm = u''
    for e in emoji.as_map():
       norm += code_point_to_unicode(e[1]) #e[0] #
    return norm
'''

def getNumberOfEmojisInString(text_uni):
    return len(splitEmojisUni(text_uni, normalize=True))

def getNumberOfEmojisInString_via_emoji_unicode_lib(text_uni):
    emoji = Emoji(text_uni)
    return len(emoji.as_map())

def getNormalizedEmojiUtf_via_emoji_unicode_lib(text_utf):
    textuni = text_utf.decode('utf-8')
    emoji = Emoji(textuni)
    norm = u''
    for e in emoji.as_map():
       norm += code_point_to_unicode(e[1]) #e[0] #
    return norm.encode('utf-8')



###
## TO MOVE INTO GLOSS
###

def getRandomItalianTag(italian=True):
    import gloss
    if italian:
        coinFlip = randint(0,1)
        if coinFlip==0:
            return TEXT_TO_EMOJI_TABLE_IT.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_IT) - 1)]
        else:
            g = gloss.getRandomGloss()
            it_words = g.target_text
            index = randint(0, len(it_words) - 1)
            return  it_words[index].encode('utf-8')
    else:
        return TEXT_TO_EMOJI_TABLE_EN.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_EN) - 1)]


def getRandomGlossTag():
    import gloss
    g = gloss.getRandomGloss()
    it_words = g.target_text
    index = randint(0, len(it_words) - 1)
    return it_words[index].encode('utf-8')

def getRandomItalianEmoji():
    import gloss
    coinFlip = randint(0, 1)
    if coinFlip == 0:
        return getRandomSingleEmoji()
    else:
        g = gloss.getRandomGloss()
        return g.source_emoji.encode('utf-8')

def getRandomGlossEmoji():
    import gloss
    g = gloss.getRandomGloss()
    return g.source_emoji.encode('utf-8')

def getRandomGlossMultiEmoji(escludeStar = True):
    import gloss
    while True:
        g = gloss.getRandomGloss()
        if getNumberOfEmojisInString(g.source_emoji)>1 and (not escludeStar or '*' not in g.getEmoji()):
            return g

def checkForGlossUniProblems():
    import gloss
    qry = gloss.Gloss.query()
    result = []
    for g in qry:
        emoji = g.source_emoji
        if not stringHasOnlyStandardEmojis(emoji.encode('utf-8')):
            result.append(g)
    return result


#def stringHasOnlyStandardEmojis(text):
#    return getStringWithoutStandardEmojis(text) == ''

#def stringHasOnlyStandardEmojis(text):
#    textuni = text.decode('utf-8')
#    comp = u''
#    for c in textuni:
#        if c not in emoji_tables.ALL_EMOJIS:
#            comp += c
#            if comp in emoji_tables.ALL_EMOJIS:
#                comp = u''
#    return comp==u''


'''
see also:
http://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
ftp://ftp.unicode.org/Public/emoji/1.0/emoji-data.txt
http://unicode.org/emoji/charts/full-emoji-list.html
https://github.com/nitely/emoji-unicode
https://github.com/iamcal/emoji-data
see pyton package unicodedat: http://stackoverflow.com/questions/2039140/python-re-how-do-i-match-an-alpha-character

old...
https://github.com/leandrotoledo/python-telegram-bot/blob/master/telegram/emoji.py
http://apps.timwhitlock.info/emoji/tables/unicode
http://www.iemoji.com/view/emoji/182/places/regional-indicator-symbol-letters-de
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/emoji.py
'''
