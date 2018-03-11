# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
import urllib2
import csv
import logging
import re
import emoji_tables

COSTITUZIONE_ICON = '📜'

class CostituzioneSentence(ndb.Model):
    #id = sentence number
    chapter = ndb.IntegerProperty()
    article = ndb.IntegerProperty()
    sentence = ndb.IntegerProperty()
    word_text = ndb.StringProperty()
    emoji_text = ndb.StringProperty()

    def getEmojiText(self):
        return self.emoji_text.encode('utf-8')

    def getWordText(self):
        return self.word_text.encode('utf-8')

def getSentenceUniqueId(chapter, article, sentence):
    return "{}:{}:{}".format(chapter, article, sentence)

def addSentence(chapter, article, sentence, word_text, emoji_text, put=False):
    cs = CostituzioneSentence(
        id=getSentenceUniqueId(chapter, article, sentence),
        chapter = chapter,
        article = article,
        sentence = sentence,
        word_text = word_text,
        emoji_text = emoji_text
    )
    if put:
        cs.put()
    return cs

def getSentenceByUniqueId(id):
    return CostituzioneSentence.get_by_id(id)

def splitUniqueId(idString):
    chapter, article, sentence = idString.split(':')
    return int(chapter), int(article), int(sentence)

def getSentenceEmojiString(id):
    cs = CostituzioneSentence.get_by_id(id)
    header = "{} Art. {}:{}".format(COSTITUZIONE_ICON,cs.article,cs.sentence)
    return "{}\n\n{}\n\n{}".format(header, cs.getWordText(), cs.getEmojiText())
    #return "{}\n\n{}".format(cs.getWordText(), cs.getEmojiText())

def getNextSentenceId(id):
    if id == "0:0:0":
        return "1:1:1"
    chapter, article, sentence = splitUniqueId(id)
    new_id = getSentenceUniqueId(chapter, article, sentence + 1)
    entry = getSentenceByUniqueId(new_id)
    if entry == None:
        new_id = getSentenceUniqueId(chapter, article+1, 1)
        entry = getSentenceByUniqueId(new_id)
    if entry != None:
        return entry.key.id()
    return None

def getPrevSentenceId(id):
    if id == "1:1:1":
        return "0:0:0"
    chapter, article, sentence = splitUniqueId(id)
    new_id = getSentenceUniqueId(chapter, article, sentence - 1)
    entry = getSentenceByUniqueId(new_id)
    if entry == None or entry.sentence==0:
        entry = getLastSentenceInChapterArticle(chapter, article-1)
    if entry != None:
        return entry.key.id()
    return None

def getLastSentenceInChapterArticle(chapter,article):
    return CostituzioneSentence.query(
        CostituzioneSentence.chapter == chapter,
        CostituzioneSentence.article == article,
    ).order(-CostituzioneSentence.sentence).get()

def populateSentences():
    tuples = getCostituzioneFromGdoc()
    to_add = []
    for t in tuples:
        chapter, article, sentence, words_sentence, emojis_sentence = t
        emoji_text = ''.join(emojis_sentence)
        ps = addSentence(chapter, article, sentence, words_sentence, emoji_text, put=False)
        to_add.append(ps)
    ndb.put_multi(to_add)
    return "Successfully added {} sentences.".format(len(tuples))

def deleteAllSentences():
    delete_futures = ndb.delete_multi_async(
        CostituzioneSentence.query().fetch(keys_only=True)
    )
    ndb.Future.wait_all(delete_futures)


# ================================
# import functions
# ================================

COSTITUZIONE_DOC_KEY = '1HFE12mO2CsBQOxg-XG2IKUTnT69B3bgy7PwqqJ8n7SQ'
COSTITUZIONE_GLOSS_DOC_KEY = '1Gjy23bp_GizhcVzHWRlF7ZQu6X049010UJQtynjOBBw'

GDOC_TSV_BASE_URL = "https://docs.google.com/spreadsheets/d/{0}/export?format=tsv&gid=0"

def getCostituzioneFromGdoc():
    result = []
    url = GDOC_TSV_BASE_URL.format(COSTITUZIONE_DOC_KEY)
    spreadSheetTsv = urllib2.urlopen(url)
    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in spreadSheetReader:
        chapter = int(row[0])
        article = int(row[1])
        sentence = int(row[2])
        words_sentence = row[3]
        emojis_sentence = tokenize(row[4])
        tuple = (chapter, article, sentence, words_sentence, emojis_sentence)
        result.append(tuple)
    return result

def tokenize(text):
    return [x.strip() for x in re.split("([\s_,;.:!?\"'])",text.strip()) if x.strip()!='' and x.strip()!=' ']

# to be called as print(costituzione.checkNormalization())
def checkNormalization():
    exceptions = []
    tuples = getCostituzioneFromGdoc()
    for l, line in enumerate(tuples, start=1):
        emojiLine = line[4]
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

# EMOJI_NORMALIZATION_TABLE = {
#     "◀️": "◀",
#     "▶️": "▶",
#     "#️⃣": "#⃣",
#     "*️⃣": "*⃣",
#     "0️⃣": "0⃣",
#     "1️⃣": "1⃣",
#     "2️⃣": "2⃣",
#     "3️⃣": "3⃣",
#     "4️⃣": "4⃣",
#     "5️⃣": "5⃣",
#     "6️⃣": "6⃣",
#     "7️⃣": "7⃣",
#     "8️⃣": "8⃣",
#     "9️⃣": "9⃣",
#     "ℹ️": "ℹ",
#     "↩️": "↩",
#     "↪️": "↪",
#     "⤵️": "⤵",
#     "⤴️": "⤴",
#     "↗️": "↗",
#     "⬆️": "⬆",
#     "➡️": "➡",
#     "↘️": "↘",
#     "⬇️": "⬇",
#     "↙️": "↙",
#     "⬅️": "⬅",
#     "↖️": "↖",
#     "↕️": "↕",
#     "↔️": "↔",
#     "↪️": "↪",
#     "↩️": "↩",
#     "♨️": "♨",
#     "🏭️": "🏭",
#     "🔲": "🔲",
#     "‼️": "‼",
#     "❗️": "❗",
#     "⁉️": "⁉",
#     "✔️": "✔",
#     "♒️": "♒",
#     "⚠️": "⚠",
#     "🍒️": "🍒",
#     "⚡️": "⚡",
#     "✴️": "✴",
#     "☝️️": "☝",
#     "⭐️": "⭐",
#     "〽️": "〽",
#     "️⚖️": "⚖",
#     "⚓️":"⚓",
#     "⛔️":"⛔",
#     "✂️": "✂",
#     "⛪️":"⛪",
#     "⚪️":"⚪",
#     "❤️":"❤",
#     "✍️️":"✍",
#     "☮️":"☮"
# }

# def normalizeEmojisWithTable(text_utf):
#     for find, replace in EMOJI_NORMALIZATION_TABLE.iteritems():
#         text_utf = text_utf.replace(find, replace)
#     return text_utf

def splitEmojiString(text):
    import emojiUtil
    if re.match("^[_,;.:!?\"']$",text):
        return [text]
    #text = normalizeEmojisWithTable(text)
    text = emojiUtil.normalizeEmojiText(text)
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