# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import ndb
import pinocchio

READY_CHAPTERS = [1]
PINOCCHIO = u'\U0001F3C3'.encode('utf-8')

class PinocchioSentence(ndb.Model):
    chapter = ndb.IntegerProperty()
    line = ndb.IntegerProperty()
    word_text = ndb.StringProperty()
    emoji_text = ndb.StringProperty()

    def getEmojiText(self):
        return self.emoji_text.encode('utf-8')

    def getWordText(self):
        return self.word_text.encode('utf-8')

def getSentenceUniqueId(chapter, line):
    return "{}:{}".format(chapter,line)

def splitUniqueId(idString):
    chapter, line = idString.split(':')
    return int(chapter), int(line)

def getNextSentenceIdString(idString):
    chapter, line = splitUniqueId(idString)
    s = getSentenceByChapterAndLineNumber(chapter, line+1)
    if s == None:
        s = getSentenceByChapterAndLineNumber(chapter+1, 1)
        # could be None if end of book
    if s != None:
        return s.key.id()
    return None

def getPrevSentenceIdString(idString):
    chapter, line = splitUniqueId(idString)
    s = getSentenceByChapterAndLineNumber(chapter, line-1)
    if s == None:
        s = getLastSentenceInChapter(chapter-1)
        # could be None if end of book
    if s != None:
        return s.key.id()
    return None

def getSentenceEmojiString(idString):
    ps = getSentenceByUniqueId(idString)
    header = "{}{}".format(PINOCCHIO,idString)
    return "{}\n\n{}\n\n{}".format(header, ps.getWordText(), ps.getEmojiText())

def addSentence(chapter, line, word_text, emoji_text, put=False):
    ps = PinocchioSentence(
        id=getSentenceUniqueId(chapter, line),
        chapter = chapter,
        line = line,
        word_text = word_text,
        emoji_text = emoji_text
    )
    if put:
        ps.put()
    return ps

def getSentenceByChapterAndLineNumber(chapter, line):
    id = getSentenceUniqueId(chapter, line)
    return PinocchioSentence.get_by_id(id)

def getSentenceByUniqueId(id):
    return PinocchioSentence.get_by_id(id)

def getLastSentenceInChapter(chapter):
    PinocchioSentence.query(PinocchioSentence.chapter==chapter).order(-PinocchioSentence.line).get()

def populatePinocchioSentences(chapter_number):
    chapter_sentences = pinocchio.getPinocchioChapters()[chapter_number - 1]
    to_add = []
    for line, row in enumerate(chapter_sentences, start=1):
        word_text = row[0]
        emoji_text = ''.join(row[1])
        ps = addSentence(chapter_number, line, word_text, emoji_text, put=False)
        to_add.append(ps)
    ndb.put_multi(to_add)
    return "Successfully added {} sentences of chapter {}.".format(len(chapter_sentences), chapter_number)
