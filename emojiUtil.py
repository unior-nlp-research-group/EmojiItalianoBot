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

def getCodePointUpperUni(e_uni, separator='-'):
    codePoints = [str(hex(ord(c)))[2:] for c in e_uni]
    codePoints = [x if len(x)>2 else "00" + x for x in codePoints]
    result = separator.join(codePoints)
    return result.upper()

def getCodePointUpper(e, separator='-'):
    return getCodePointUpperUni(e.decode('utf-8'), separator)

ALL_EMOJIS = [getEmojiFromCodePoint(entry['unified']) for entry in EMOJI_INFO]
EMOJI_CODE_POINT_WITH_SKIN_TONES = [entry['unified'] for entry in EMOJI_INFO if 'skin_variations' in entry]
UNIFIED_CODE_POINTS = [entry['unified'] for entry in EMOJI_INFO if entry['unified']!=None]
NON_QUALIFIED_CODE_POINTS = [entry['non_qualified'] for entry in EMOJI_INFO if entry['non_qualified']!=None]

SKIN_TONES = ['🏻', '🏾', '🏿', '🏼', '🏽']
SKIN_TONES_CODE_POINT = [getCodePointUpper(x) for x in SKIN_TONES]

def containsSkinTone(emoji_text):
    return any(st in emoji_text for st in SKIN_TONES)

def removeSkinTones(emoji_text):
    for st in SKIN_TONES:
        emoji_text = emoji_text.replace(st, '')
    return emoji_text

def makeCodePointUnified(code_point):
    try:
        entry = next(x for x in EMOJI_INFO if x['non_qualified']==code_point)
    except StopIteration:
        return None
    return entry['unified']

def getRandomEmoji():
    return random.choice(ALL_EMOJIS)


def checkIfValidEmoji(uni_e, normalize):
    code_point = getCodePointUpperUni(uni_e)
    if code_point in UNIFIED_CODE_POINTS:
        return uni_e, True
    if normalize:
        if code_point in NON_QUALIFIED_CODE_POINTS:
            code_point = makeCodePointUnified(code_point)
            uni_e = getEmojiFromCodePoint(code_point).decode('utf-8')
            return uni_e, True
        code_point_split = code_point.split('-')
        if len(code_point_split)>1 and code_point_split[-1] in SKIN_TONES_CODE_POINT:
            code_point_without_skin_color = '-'.join(code_point_split[0:-1])
            if code_point_without_skin_color in EMOJI_CODE_POINT_WITH_SKIN_TONES:
                uni_e = getEmojiFromCodePoint(code_point_without_skin_color).decode('utf-8')
                return uni_e, True
    return uni_e, False

# returns None if any emoji is not recognized
def splitEmojis(text_utf, normalize=True):
    parts = []
    textuni = text_utf.decode('utf-8')
    s = 0
    e = len(textuni)
    while(True):
        span = textuni[s:e]
        #print "span:{} s:{} e:{}".format(getCodePointUpper(span.encode('utf-8')), s, e)
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

#def stringHasOnlyStandardEmojis(text):
#    return splitEmojis(text, normalize=False) is not None

def normalizeEmojiText(text_utf):
    parts = splitEmojis(text_utf)
    if parts is None:
        return None
    return ''.join(parts)


def stringContainsAnyStandardEmoji(text):
    return any(e in text for e in ALL_EMOJIS)

####################################
# EMOJI IMG UTIL FUNCTIONS
####################################

EMOJI_PNG_URL = 'https://github.com/iamcal/emoji-data/raw/master/img-twitter-72/'

def getEmojiImageDataFromUrl(e):
    codePointUpper = getCodePointUpper(e)
    if e not in ALL_EMOJIS:
        codePointUpper = makeCodePointUnified(codePointUpper)
        if codePointUpper is None:
            logging.debug('Unknown emoji {} {}'.format(e, codePointUpper))
            return None
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

