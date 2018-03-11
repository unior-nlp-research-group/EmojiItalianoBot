# -*- coding: utf-8 -*-

import logging
import jsonUtil
import random
import emojiTags

# imported from https://github.com/iamcal/emoji-data/blob/master/emoji_pretty.json
EMOJI_JSON_FILE = 'EmojiData/emoji_pretty.json'
EMOJI_INFO = jsonUtil.json_load_byteified_file(EMOJI_JSON_FILE)

def getEmojiFromCodePoint(code_point, separator='-'):
    codes = code_point.split(separator)
    emoji_uni = ''.join(unichr(int(c,16)) for c in codes)
    emoji_utf = emoji_uni.encode('utf-8')
    return emoji_utf

ALL_EMOJIS = [getEmojiFromCodePoint(entry['unified']) for entry in EMOJI_INFO]
UNIFIED_CODE_POINTS = [entry['unified'] for entry in EMOJI_INFO]
NON_QUALIFIED_CODE_POINTS = [entry['non_qualified'] for entry in EMOJI_INFO]

def makeCodePointUnified(code_point):
    try:
        entry = next(x for x in EMOJI_INFO if x['non_qualified']==code_point)
    except StopIteration:
        return None
    return entry['unified']

def getCodePointUpper(e, separator='-'):
    codePoints = [str(hex(ord(c)))[2:] for c in e.decode('utf-8')]
    codePoints = [x if len(x)>2 else "00" + x for x in codePoints]
    result = separator.join(codePoints)
    return result.upper()

def getCodePointUpperUni(e_uni, separator='-'):
    codePoints = [str(hex(ord(c)))[2:] for c in e_uni]
    codePoints = [x if len(x)>2 else "00" + x for x in codePoints]
    result = separator.join(codePoints)
    return result.upper()


def checkIfEmojiAndGetNormalized(e):
    if e in ALL_EMOJIS:
        return e
    code_point = getCodePointUpper(e)
    if code_point in NON_QUALIFIED_CODE_POINTS:
        fixed_code_point = makeCodePointUnified(code_point)
        e = getEmojiFromCodePoint(fixed_code_point)
        return e
    return None

def getRandomEmoji():
    return random.choice(ALL_EMOJIS)


####################################
# EMOJI IMG UTIL FUNCTIONS
####################################

EMOJI_PNG_URL = 'https://github.com/iamcal/emoji-data/raw/master/img-twitter-72/'

def getEmojiImageDataFromUrl(e):
    codePointUpper = getCodePointUpper(e)
    if e not in ALL_EMOJIS:
        unifiedUpper = makeCodePointUnified(codePointUpper)
        codePointUpper = unifiedUpper
    emojiUrl = EMOJI_PNG_URL + codePointUpper.lower() + ".png"
    logging.debug('Requesting emoj url: ' + emojiUrl)
    return emojiUrl

def getEmojiStickerDataFromUrl(e):
    import requests
    from google.appengine.api import images
    png_url = getEmojiImageDataFromUrl(e)
    png_data = requests.get(png_url).content
    sticker_data = images.crop(image_data=png_data, left_x=0.0, top_y=0.0,
        right_x=1.0, bottom_y=1.0, output_encoding=images.WEBP)
    return sticker_data


# =============================
# Check Emoji image Files and Url
# =============================

def checkAllEmojiUrl():
    import requests
    total = 0
    error = 0
    for e in ALL_EMOJIS:
        total += 1
        url = getEmojiImageDataFromUrl(e)
        r = requests.get(url)
        if r.status_code==200:
            print("ok: " + url)
        else:
            error += 1
    print("{0}/{1}".format(str(error),str(total)))

# =============================
# AUX FUNCTIONS
# =============================

def checkIfValidEmoji(uni_e, normalize):
    code_point = getCodePointUpperUni(uni_e)
    #print(code_point)
    if code_point in UNIFIED_CODE_POINTS:
        return uni_e, True
    if normalize and code_point in NON_QUALIFIED_CODE_POINTS:
        code_point = makeCodePointUnified(code_point)
        uni_e = getEmojiFromCodePoint(code_point).decode('utf-8')
        return uni_e, True
    return uni_e, False

'''
# uni version of splitEmojis (not needed anymore hopefully)
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
'''

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

def getNumberOfEmojisInString(text_utf):
    return len(splitEmojis(text_utf, normalize=True))

def stringHasOnlyStandardEmojis(text):
    return splitEmojis(text, normalize=False) is not None

def normalizeEmojiText(text_utf):
    parts = splitEmojis(text_utf)
    if parts is None:
        return None
    return ''.join(parts)

def stringContainsAnyStandardEmoji(text):
    return any(e in text for e in ALL_EMOJIS)

def getRandomSingleEmoji(italian=True, escludeStar = True):
    dict = emojiTags.EMOJI_TAGS_IT if italian else emojiTags.EMOJI_TAGS_EN
    while True:
        result = random.choice(dict.keys())
        if not escludeStar or '*' not in result:
            return result


def getRandomTag(italian=True):
    dict = emojiTags.EMOJI_TAGS_IT if italian else emojiTags.EMOJI_TAGS_EN
    while True:
        e, tag_list = random.choice(dict.items())
        if len(tag_list)>0:
            return random.choice(tag_list)


'''
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

def getEmojisForTag(tag, italian=True):
    tagLowerCase = tag.lower()
    if italian:
        return TEXT_TO_EMOJI_TABLE_IT.get(tagLowerCase)
    return TEXT_TO_EMOJI_TABLE_EN.get(tagLowerCase)

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

def getStringWithoutStandardEmojis(text):
    textuni = text.decode('utf-8')
    return emoji_tables.emoji_pattern.sub('', textuni).encode('utf-8')  # no emoji

'''

'''
def getNormalizedEmojiUni_via_emoji_unicode_lib(text_uni):
    emoji = Emoji(text_uni)
    norm = u''
    for e in emoji.as_map():
       norm += code_point_to_unicode(e[1]) #e[0] #
    return norm
'''

'''

def getNumberOfEmojisInString_via_emoji_unicode_lib(text_uni):
    from emoji_unicode import Emoji
    emoji = Emoji(text_uni)
    return len(emoji.as_map())

def getNormalizedEmojiUtf_via_emoji_unicode_lib(text_utf):
    from emoji_unicode import Emoji
    from emoji_unicode.utils import code_point_to_unicode, unicode_to_code_point
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
