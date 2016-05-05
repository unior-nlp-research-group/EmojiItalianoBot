import logging
from google.appengine.ext import ndb
from random import randint, shuffle

import emojiUtil

class Gloss(ndb.Model):
    source_emoji = ndb.StringProperty()
    target_text = ndb.StringProperty(repeated=True)
    modify_by_chat_id = ndb.IntegerProperty(repeated=True)
    last_mod = ndb.DateTimeProperty(auto_now=True)
    counter = ndb.IntegerProperty()

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
    return g.source_emoji.encode('utf-8') + "|" + str(g.target_text)

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

'''
#TO USE ONLY ONCE
def addIncrementalCounter():
    qry = Gloss.query()
    count = 0
    for g in qry:
        count += 1
        g.counter = count
        g.put()
    idManager = GlossEntryNumberManager(
        id=GLOSS_MANAGER_SINGLETON,
        count=count,
        gaps=[]
    )
    idManager.put()
    return count
'''

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

def checkForGlossUniProblems():
    qry = Gloss.query()
    result = []
    for g in qry:
        emoji = g.source_emoji
        if not emojiUtil.stringHasOnlyStandardEmojis(emoji.encode('utf-8')):
            result.append(g)
    return result