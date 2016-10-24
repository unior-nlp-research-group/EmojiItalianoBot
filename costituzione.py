# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import urllib2
import csv
import logging
import re
import emoji_tables

COSTITUZIONE_ICON = '📜'

class CostituzinoeSentence(ndb.Model):
    #id = sentence number
    word_text = ndb.StringProperty()
    emoji_text = ndb.StringProperty()

    def getEmojiText(self):
        return self.emoji_text.encode('utf-8')

    def getWordText(self):
        return self.word_text.encode('utf-8')

def addSentence(sentenceNumber, word_text, emoji_text, put=False):
    cs = CostituzinoeSentence(
        id = sentenceNumber,
        word_text = word_text,
        emoji_text = emoji_text
    )
    if put:
        cs.put()
    return cs

def getSentenceEmojiString(id):
    cs = CostituzinoeSentence.get_by_id(id)
    #header = "{}{}".format(COSTITUZIONE_ICON,id)
    #return "{}\n\n{}\n\n{}".format(header, ps.getWordText(), ps.getEmojiText())
    return "{}\n\n{}".format(cs.getWordText(), cs.getEmojiText())

def getNextSentenceId(id):
    cs = CostituzinoeSentence.get_by_id(id+1)
    if cs:
        return cs.key.id()
    return None

def getPrevSentenceId(id):
    cs = CostituzinoeSentence.get_by_id(id-1)
    if cs:
        return cs.key.id()
    return None

def populateSentences():
    sentences = getCostituzioneSentences()
    to_add = []
    for n, row in enumerate(sentences, start=1):
        word_text = row[0]
        emoji_text = ''.join(row[1])
        ps = addSentence(n, word_text, emoji_text, put=False)
        to_add.append(ps)
    ndb.put_multi(to_add)
    return "Successfully added {} sentences.".format(len(sentences))

def deleteAllSentences():
    delete_futures = ndb.delete_multi_async(
        CostituzinoeSentence.query().fetch(keys_only=True)
    )
    ndb.Future.wait_all(delete_futures)


# ================================
# import functions
# ================================

COSTITUZIONE_DOC_KEY = '1HFE12mO2CsBQOxg-XG2IKUTnT69B3bgy7PwqqJ8n7SQ'
COSTITUZIONE_GLOSS_DOC_KEY = '1Gjy23bp_GizhcVzHWRlF7ZQu6X049010UJQtynjOBBw'

GDOC_TSV_BASE_URL = "https://docs.google.com/spreadsheets/d/{0}/export?format=tsv&gid=0"

def getCostituzioneSentences():
    sentences = []
    url = GDOC_TSV_BASE_URL.format(COSTITUZIONE_DOC_KEY)
    spreadSheetTsv = urllib2.urlopen(url)
    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in spreadSheetReader:
        words_sentence = row[0]
        emojis_sentence = tokenize(row[1])
        sentence = (words_sentence, emojis_sentence)
        sentences.append(sentence)
    return sentences

def tokenize(text):
    return [x.strip() for x in re.split("([\s_,;.:!?\"'])",text.strip()) if x.strip()!='' and x.strip()!=' ']

def checkNormalization():
    exceptions = []
    sentences = getCostituzioneSentences()
    for l, line in enumerate(sentences, start=1):
        emojiLine = line[1]
        try:
            splitEmojiLine(emojiLine)
        except Exception as error:
            msg = str(error) + " in line " + str(l)
            exceptions.append(msg)
            #if len(exceptions)==10:
            #    return '\n'.join(exceptions)
    if exceptions:
        return '\n'.join(exceptions)
        #return exceptions
    return "All OK!"

def splitEmojiLine(emoji_punct_list):
    result = []
    for i, e in enumerate(emoji_punct_list):
        eList = splitEmojiString(e)
        if eList:
            result.extend(eList)
        else:
            raise Exception('Problem in splitting {} in position {}'.format(e, i))
    return result

EMOJI_NORMALIZATION_TABLE = {
    "◀️": "◀",
    "▶️": "▶",
    "#️⃣": "#⃣",
    "*️⃣": "*⃣",
    "0️⃣": "0⃣",
    "1️⃣": "1⃣",
    "2️⃣": "2⃣",
    "3️⃣": "3⃣",
    "4️⃣": "4⃣",
    "5️⃣": "5⃣",
    "6️⃣": "6⃣",
    "7️⃣": "7⃣",
    "8️⃣": "8⃣",
    "9️⃣": "9⃣",
    "ℹ️": "ℹ",
    "↩️": "↩",
    "↪️": "↪",
    "⤵️": "⤵",
    "⤴️": "⤴",
    "↗️": "↗",
    "⬆️": "⬆",
    "➡️": "➡",
    "↘️": "↘",
    "⬇️": "⬇",
    "↙️": "↙",
    "⬅️": "⬅",
    "↖️": "↖",
    "↕️": "↕",
    "↔️": "↔",
    "↪️": "↪",
    "↩️": "↩",
    "♨️": "♨",
    "🏭️": "🏭",
    "🔲": "🔲",
    "‼️": "‼",
    "❗️": "❗",
    "⁉️": "⁉",
    "✔️": "✔",
    "♒️": "♒",
    "⚠️": "⚠",
    "🍒️": "🍒",
    "⚡️": "⚡",
    "✴️": "✴",
    "☝️️": "☝",        
    "⭐️": "⭐",
    "〽️": "〽", 
    "️⚖️": "⚖",   
    "⚓️":"⚓",
    "⛔️":"⛔",
    "✂️": "✂",
    "⛪️":"⛪",
    "⚪️":"⚪",
    "❤️":"❤"    
}

def normalizeEmojisWithTable(text_utf):
    for find, replace in EMOJI_NORMALIZATION_TABLE.iteritems():
        text_utf = text_utf.replace(find, replace)
    return text_utf

def normalizeEmojis(text_utf):
    import emojiUtil
    text_uni = text_utf.decode('utf-8')
    norm_uni = emojiUtil.getNormalizedEmojiUni(text_uni)
    return norm_uni.encode('utf-8')

def splitEmojiString(text):    
    if re.match("^[_,;.:!?\"']$",text):
        return [text]
    text = normalizeEmojisWithTable(text)
    #text = normalizeEmojis(text)
    parts = []
    if len(text) == 0:
        return parts
    textuni = text.decode('utf-8')
    s = 0
    e = len(textuni)
    while(True):
        span = textuni[s:e]
        #span = emojiUtil.getNormalizedEmojiUni(span)
        if span in emoji_tables.ALL_EMOJIS:
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