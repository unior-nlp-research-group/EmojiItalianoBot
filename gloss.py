# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from random import randint, shuffle

import csv
import date_util
from operator import itemgetter

import webapp2
import json
from collections import defaultdict

class Gloss(ndb.Model):
    source_emoji = ndb.StringProperty()
    target_text = ndb.StringProperty(repeated=True)
    modify_by_chat_id = ndb.IntegerProperty(repeated=True)
    last_mod = ndb.DateTimeProperty(auto_now=True)
    counter = ndb.IntegerProperty()

    def getEmoji(self):
        return self.source_emoji.encode('utf-8')

    def getFirstTranslation(self):
        return self.target_text[0].encode('utf-8')

    def getGlossTags(self):
        return [x.encode('utf-8') for x in self.target_text]

GLOSS_MANAGER_SINGLETON = "GLOSS_COUNTER_MANAGER"

class GlossEntryNumberManager(ndb.Model):
    """Shards for the counter"""
    count = ndb.IntegerProperty(default=0)
    gaps = ndb.IntegerProperty(repeated=True)

def getNextGlossEntryNumber():
    idManager = GlossEntryNumberManager.get_by_id(GLOSS_MANAGER_SINGLETON)
    if idManager.gaps:
        result = idManager.gaps.pop()
    else:
        idManager.count += 1
        result = idManager.count
    idManager.put()
    return result

def getNumberingGaps():
    idManager = GlossEntryNumberManager.get_by_id(GLOSS_MANAGER_SINGLETON)
    return idManager.gaps


def getRandomGloss():
    idManager = GlossEntryNumberManager.get_by_id(GLOSS_MANAGER_SINGLETON)
    while(True):
        random_index = randint(1,idManager.count)
        if random_index in idManager.gaps:
            continue
        g = Gloss.query(Gloss.counter == random_index).get()
        if g:
            return g
        else:
            logging.warning("Problem in fetching random index: " + str(random_index))
    return g

def getGlosEmojiAndTargetText(g):
    return g.source_emoji.encode('utf-8') + "|" + str(g.getGlossTags())

def getConfusionTranslations(correctG, size):
    index = randint(0, len(correctG.target_text)-1)
    selected_tranlation = correctG.target_text[index]
    options = [selected_tranlation]
    for i in range(1,size):
        while(True):
            randomG = getRandomGloss()
            if randomG.source_emoji != correctG.source_emoji:
                index = randint(0, len(randomG.target_text) - 1)
                selected_random_tranlation = randomG.target_text[index]
                options.append(selected_random_tranlation)
                break
    options = [x.encode('utf-8') for x in options]
    shuffle(options)
    return options

def getConfusionEmoji(correctG, size):
    options = [correctG.source_emoji]
    for i in range(1, size):
        while (True):
            randomG = getRandomGloss()
            if randomG.source_emoji != correctG.source_emoji:
                options.append(randomG.source_emoji)
                break
    options = [x.encode('utf-8') for x in options]
    shuffle(options)
    return options

def addGloss(person, source_emoji, target_word):
    g = Gloss()
    g.populate(source_emoji=source_emoji, target_text = [target_word],
               modify_by_chat_id=[person.chat_id], counter = getNextGlossEntryNumber())
    g.put()
    return g

def appendTargetText(person, gloss, target_word):
    gloss.target_text.append(target_word)
    if person.chat_id not in gloss.modify_by_chat_id:
        gloss.modify_by_chat_id.append(person.chat_id)
    gloss.put()
    return gloss

def deleteGloss(gloss):
    number = gloss.counter
    idManager = GlossEntryNumberManager.get_by_id(GLOSS_MANAGER_SINGLETON)
    if number == idManager.count:
        #last eleement, no need to add gap
        idManager.count -= 1
    else:
        idManager.gaps.append(number)
    idManager.put()
    gloss.key.delete()

def deleteEntry(person, gloss, target_word):
    target_word_decode = target_word.decode('utf-8')
    if target_word_decode in gloss.target_text:
        gloss.target_text.remove(target_word_decode)
        if person.chat_id not in gloss.modify_by_chat_id:
            gloss.modify_by_chat_id.append(person.chat_id)
        gloss.put()
        return True
    return False

def getTextFromEmoji(source_emoji):
    souce_emoji_uni = source_emoji.decode('utf-8')
    g = Gloss.query(Gloss.source_emoji == souce_emoji_uni).get()
    if g:
        return g.target_text
    return None

def getGlossFromEmoji(source_emoji):
    g = Gloss.query(Gloss.source_emoji == source_emoji).get()
    return g

def getGloss(source_emoji, target_word):
    g = Gloss.query(Gloss.source_emoji == source_emoji).get()
    if g and target_word.decode('utf-8') in g.target_text:
        return g
    return None


def getEmojiListFromText(target_text):
    target_text_uni = target_text.decode('utf-8')
    result = []
    qry = Gloss.query(Gloss.target_text.IN([target_text_uni]))
    for g in qry:
        result.append(g.source_emoji.encode('utf-8'))
    return result


def hasText(target_text):
    return Gloss.query(Gloss.target_text.IN([target_text])).get() is not None

def hasEmoji(source_emoji):
    return Gloss.query(Gloss.source_emoji == source_emoji).get() is not None

def getEmojiTranslationsCount():
    qry = Gloss.query()
    emojiCount = 0
    translationCount = 0
    for g in qry:
        emojiCount +=1
        translationCount += len(g.target_text)
    return (emojiCount, translationCount)


#################
# UPDATE SPREADSHEET DATA
# remote_api_shell.py -s emojitalianobot.appspot.com
#################

def getGlossTableRows():
    rows = []
    for g in Gloss.query().fetch():
        rows.append(
            (
                g.getEmoji(),
                ", ".join(g.getGlossTags()),
                date_util.dateString(g.last_mod)
            )
        )
    rows = sorted(rows, key=itemgetter(0))
    return rows

def getGlossTableRowsInverted():
    wordEmojiTable = defaultdict(list)
    wordEmojiLasMod = defaultdict(lambda: date_util.get_date_long_time_ago())
    for g in Gloss.query().fetch():
        for w in g.getGlossTags():
            wordEmojiTable[w].append(g.getEmoji())
            wordEmojiLasMod[w] = max(wordEmojiLasMod[w],g.last_mod)
    rows = []
    for w, eList in wordEmojiTable.iteritems():
        rows.append(
            (
                w,
                ", ".join(eList),
                date_util.dateString(wordEmojiLasMod[w])
            )
        )
    rows = sorted(rows, key=itemgetter(0))
    return rows

def exportToCsv():
    csvFileName = "/Users/fedja/Downloads/gloss.csv"

    rows = getGlossTableRows()

    with open(csvFileName, 'wb') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for r in rows:
            csvWriter.writerow(r)
    print 'Finished saving ' + str(len(rows)) + ' rows.'

class GlossarioTableJson(webapp2.RequestHandler):
    def get(self):
        result = [
            {
            'emoji': row[0],
            'parole': row[1],
            'data ultima modifica': row[2]
            } for row in getGlossTableRows()
        ]
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.out.write(json.dumps(result, indent=4, ensure_ascii=False))

def getGlossarioHtml(inverted=False):
    fileds = ['Emoji','Parola']
    if inverted:
        fileds.reverse()
    htmlText = "<html><body>"
    htmlText += '<p>Ultimo aggiornamento: {}</p>'.format(date_util.dateTimeString())
    htmlText += '\n<br>\n'
    htmlText += \
        """
        <table border = "1">
        <tr>
            <th width="100px">{}</th>
            <th width="400px">{}/e</th>
            <th width="100px">Data ultima modifica</th>
        </tr>
        """.format(fileds[0],fileds[1])
    table = getGlossTableRowsInverted() if inverted else getGlossTableRows()
    for row in table:
        htmlText += \
            """
            <table border = "1">
            <tr>
                <td width="100px">{}</td>
                <td width="400px">{}</td>
                <td width="100px">{}</td>
            </tr>
            """.format(row[0], row[1], row[2])
    htmlText += '</table>'
    htmlText += "</body></html>"
    return htmlText

class GlossarioTableHtml(webapp2.RequestHandler):
    def get(self):
        htmlText = getGlossarioHtml()
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(htmlText)

class GlossarioTableHtmlInverted(webapp2.RequestHandler):
    def get(self):
        htmlText = getGlossarioHtml(inverted=True)
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(htmlText)
