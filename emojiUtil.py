# -*- coding: utf-8 -*-

import logging
import re
import json
import emoji_tables
from emoji_unicode import Emoji
from emoji_unicode.utils import code_point_to_unicode
from collections import defaultdict
from random import randint

import gloss

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

def getRandomItalianTag(italian=True):
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

def getRandomUnicodeTag(italian=True):
    if italian:
        return TEXT_TO_EMOJI_TABLE_IT.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_IT) - 1)]
    else:
        return TEXT_TO_EMOJI_TABLE_EN.keys()[randint(1, len(TEXT_TO_EMOJI_TABLE_EN) - 1)]

def getRandomGlossTag():
    g = gloss.getRandomGloss()
    it_words = g.target_text
    index = randint(0, len(it_words) - 1)
    return it_words[index].encode('utf-8')

def getRandomItalianEmoji():
    coinFlip = randint(0, 1)
    if coinFlip == 0:
        return getRandomSingleEmoji()
    else:
        g = gloss.getRandomGloss()
        return g.source_emoji.encode('utf-8')

def getRandomGlossEmoji():
    g = gloss.getRandomGloss()
    return g.source_emoji.encode('utf-8')

def getRandomGlossMultiEmoji():
    while True:
        g = gloss.getRandomGloss()
        if getNumberOfEmojisInString(g.source_emoji)>1:
            return g

def getRandomSingleEmoji(italian=True):
    if italian:
        return EMOJI_TO_TEXT_TABLE_IT.keys()[randint(1, len(EMOJI_TO_TEXT_TABLE_IT) - 1)]
    else:
        return EMOJI_TO_TEXT_TABLE_EN.keys()[randint(1, len(EMOJI_TO_TEXT_TABLE_EN) - 1)]

##################
## FUNCTIONS
##################

def getStringWithoutStandardEmojis(text):
    textuni = text.decode('utf-8')
    return emoji_tables.emoji_pattern.sub('', textuni).encode('utf-8')  # no emoji

def stringHasOnlyStandardEmojis(text):
    if len(text)==0:
        return True
    textuni = text.decode('utf-8')
    comp = u''
    s = 0
    e = len(textuni)
    while(True):
        #print("s=%s e=%s str=%s" % (str(s), str(e),textuni[s:e]))
        if textuni[s:e] in emoji_tables.ALL_EMOJIS:
            if e == len(textuni):
                return True
            textuni = textuni[e:]
            s = 0
            e = len(textuni)
        else:
            e -= 1
            if s==e:
                return False

def getNormalizedEmoji(text):
    textuni = text.decode('utf-8')
    emoji = Emoji(textuni)
    norm = u''
    for e in emoji.as_map():
       norm += code_point_to_unicode(e[1]) #e[0] #
    return norm.encode('utf-8')


def stringContainsAnyStandardEmoji(text):
    return getStringWithoutStandardEmojis(text) != text

def haveEmojisInCommon(text1, text2):
    textuni1 = text1.decode('utf-8')
    textuni2 = text2.decode('utf-8')
    m1 = re.match(emoji_tables.emoji_pattern, textuni1)
    m2 = re.match(emoji_tables.emoji_pattern, textuni2)
    if m1 and m2:
        return len(set(m1.groups()).intersection(m2.groups()))>0
    return False

def getNumberOfEmojisInString(text_uni):
    emoji = Emoji(text_uni)
    return len(emoji.as_map())

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
