# -*- coding: utf-8 -*-

import jsonUtil
import random

EMOJI_TAGS_IT = jsonUtil.json_load_byteified_file('EmojiData/emoji_tags_it.json')
EMOJI_TAGS_EN = jsonUtil.json_load_byteified_file('EmojiData/emoji_tags_en.json')

def getTagsForEmoji(emoji, italian=True):
    dict = EMOJI_TAGS_IT if italian else EMOJI_TAGS_EN
    return dict.get(emoji)

def getEmojisForTag(tag, italian=True, wordOnly=True):
    dict = EMOJI_TAGS_IT if italian else EMOJI_TAGS_EN
    if wordOnly:
        result = [e for e,tag_list in dict.items() if any(tag in t.lower().split() for t in tag_list)]
    else:
        result = [e for e, tag_list in dict.items() if any(tag in t.lower() for t in tag_list)]
    return result


def getRandomSingleEmoji(italian=True, escludeStar = True):
    dict = EMOJI_TAGS_IT if italian else EMOJI_TAGS_EN
    while True:
        result = random.choice(dict.keys())
        if not escludeStar or '*' not in result:
            return result


def getRandomTag(italian=True):
    dict = EMOJI_TAGS_IT if italian else EMOJI_TAGS_EN
    while True:
        e, tag_list = random.choice(dict.items())
        if len(tag_list)>0:
            return random.choice(tag_list)


##################
# BUILD FUNCTIONS
##################

#EXCLUDE_TAGS = ['skin tone', 'fototipo']
ANNOTATION_URL = 'http://unicode.org/repos/cldr/trunk/common/annotations/'
#ANNOTATION_DERIVED_URL = 'http://unicode.org/repos/cldr/trunk/common/annotationsDerived/'

def getEmojiLanguageTagsFromUrl(language_code):
    import emojiUtil
    import requests
    from xml.etree import ElementTree
    from collections import defaultdict
    annotation_dict = defaultdict(set)
    for base_url in [ANNOTATION_URL]: #ANNOTATION_DERIVED_URL
        url = base_url + '{}.xml'.format(language_code)
        print 'parsing {}'.format(url)
        response = requests.get(url)
        root = ElementTree.fromstring(response.content)
        for annotation in root.iter('annotation'):
            emoji = annotation.attrib['cp'].encode('utf-8')
            emoji = emojiUtil.normalizeEmojiText(emoji)
            if emoji:
                annotation_entries = [a.strip() for a in annotation.text.encode('utf-8').split('|')]
                #annotation_entries = [a for a in annotation_entries if all(tag not in a for tag in EXCLUDE_TAGS)]
                annotation_dict[emoji].update(annotation_entries)
    annotation_dict_list = {k:list(v) for k,v in annotation_dict.items()}
    return annotation_dict_list

def buildLanguageTagsFiles():
    import json
    for lang_code in ['it','en']:
        file_path = 'EmojiData/emoji_tags_{}.json'.format(lang_code)
        with open(file_path, 'w') as f:
            d = getEmojiLanguageTagsFromUrl(lang_code)
            json.dump(d, f, ensure_ascii=False, indent=4, sort_keys=True)