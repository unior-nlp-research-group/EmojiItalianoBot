# -*- coding: utf-8 -*-

import urllib2
import csv
import logging
import re

PINOCCHIO_CHAPTERS_DOC_KEYS = [
    '11mufZ56LAENBIiCXCMTHhQuqKCbFWnOpqPf_iAi35Dk', #CH 1
    '1321CXesORVKQUziGiTRofXCO1Mz2Rx8E7aV9_fUQ3p0', #CH 2
    '11HIM6sKNqJ3mtJmgeY3-17N_r5ppx8C6rRqRnelfMTg', #CH 3
    '11ppl9dK0K6ruuY020NXwAWFL9LTrdpPz2YoCeM2Z5tA', #CH 4
    '13sXU-lM0GfKpLdI_YieRdnn8TWtkIGD_NimMaSYbJVo', #CH 5
    '14TQFL04gxqaiFas_jqmSu5bVwmhg-EzPkT60V5T5HAg', #CH 6
    '154y0ukloCUY3OocmtEWQDsCVe4TYo4BybTEtdhkgssA', #CH 7
    '15POIjJU6h0pRfMKM1GEFmrrvINGdiFs5DYf1Zeu9Xt0', #CH 8
    '17UTQraqnmlasdDlEeDSboor3dLRIE1Iu23oLZNNkCWI', #CH 9
    '18MV1v2j1dRfL3mMdugZ27IVlsKdbgqYqcAXHeAl6vk8', #CH 10
]


PINOCCHIO_CHAPTER_URL = "https://docs.google.com/spreadsheets/d/{0}/export?format=tsv&gid=0"


PINOCCHIO_CHAPTERS = None

def getPinocchioChapters():
    global PINOCCHIO_CHAPTERS
    if PINOCCHIO_CHAPTERS==None:
        buildPinocchioChapters()
    return PINOCCHIO_CHAPTERS

def buildPinocchioChapters():
    global PINOCCHIO_CHAPTERS
    PINOCCHIO_CHAPTERS = []
    try:
        for i in range(0, len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
            chapterSentences = []
            url = PINOCCHIO_CHAPTER_URL.format(PINOCCHIO_CHAPTERS_DOC_KEYS[i])
            spreadSheetTsv = urllib2.urlopen(url)
            spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
            # next(spreadSheetReader)  # skip first row
            for row in spreadSheetReader:
                words_sentence = tokenize(row[0])
                emojis_sentence = tokenize(row[1])
                sentence = (words_sentence, emojis_sentence)
                chapterSentences.append(sentence)
            PINOCCHIO_CHAPTERS.append(chapterSentences)
    except Exception, e:
        logging.debug("Problem retreiving language structure from url: " + str(e))

def countLineInChapter(chapterNumber):
    url = PINOCCHIO_CHAPTER_URL.format(PINOCCHIO_CHAPTERS_DOC_KEYS[chapterNumber-1])
    spreadSheetTsv = urllib2.urlopen(url)
    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
    data = list(spreadSheetReader)
    row_count = len(data)
    return row_count

def tokenize(text):
    return [x.strip() for x in re.split("[_\s,;.!?\"']+",text.strip()) if x.strip()!='']

def findEmojiInPinocchio(emoji, deepSearch=False):
    PC = getPinocchioChapters()
    result = []
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, words_emojis_sentence in enumerate(chapter, 1):
            line_emojis = words_emojis_sentence[1]
            if emoji in line_emojis:
                result.append("{0}.{1}".format(str(ch_num),str(line_num)))
            elif deepSearch:
                for emoji_word in line_emojis:
                    if emoji_word.find(emoji)>=0:
                        result.append("{0}.{1}".format(str(ch_num), str(line_num)))
                        break
    return result
