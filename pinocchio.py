# -*- coding: utf-8 -*-

import urllib2
import csv
import logging
import re
import emoji_tables

# titoli: https://docs.google.com/spreadsheets/d/1EviZIbjoK9x3WV65S18KYZO3u39NrFsfGpbBofABN9c/edit?usp=sharing

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
    '1x1HyOx3ce_CZMkNK0DKccdjutfvjhfatB-ZfJPBcaH0', #CH 11
    '13sONpthnVc5pGd4mov5QWFXTEzAqAeYWyM4rCeVOl9Y', #CH 12
    '1BXMlU9ucARKQ46vtU2LdeD4kiZX4QkykZrNiIID02pY', #CH 13
    '1DoteODTe1cVb0fM6HGq5efWTf89V_WUzgA7p7wF-94Y', #CH 14
    '1ESMe7cB1AxqNto8UDxDMSwpySBXFWFRHXSG5yc1Z1yo', #CH 15
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
    #try:
    for i in range(0, len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
        chapterSentences = []
        url = PINOCCHIO_CHAPTER_URL.format(PINOCCHIO_CHAPTERS_DOC_KEYS[i])
        spreadSheetTsv = urllib2.urlopen(url)
        spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
        # next(spreadSheetReader)  # skip first row
        for row in spreadSheetReader:
            words_sentence = row[0] #tokenize(row[0])
            emojis_sentence = tokenize(row[1])
            sentence = (words_sentence, emojis_sentence)
            chapterSentences.append(sentence)
        PINOCCHIO_CHAPTERS.append(chapterSentences)
    #except Exception, e:
    #    logging.debug("Problem retreiving language structure from url: " + str(e))

def getPinocchioEmojiChapterSentence(chapter, sentence):
    return getPinocchioChapters()[chapter-1][sentence-1][1]

def countLineInChapter(chapterNumber):
    url = PINOCCHIO_CHAPTER_URL.format(PINOCCHIO_CHAPTERS_DOC_KEYS[chapterNumber-1])
    spreadSheetTsv = urllib2.urlopen(url)
    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
    data = list(spreadSheetReader)
    row_count = len(data)
    return row_count

def tokenize(text):
    return [x.strip() for x in re.split("([\s_,;.:!?\"'])",text.strip()) if x.strip()!='' and x.strip()!=' ']

PUNCTUATION_LATEXT_TABLE = {
    "_": r'\under',
    "'": r'\sq',
    '"': r'\dq',
    ".": r'\period',
    ":": r'\colonpunct',
    ",": r'\comma',
    ";": r'\semicolon',
    "!": r'\excl',
    "?": r'\quest',
    "(": r'\opar',
    ")": r'\cpar',
}

def getLatexParallelPinocchioChapter(chapter_number):
    chapter = getPinocchioChapters()[chapter_number - 1]
    linesInChapter = len(chapter)
    lines = []
    lines.append(r"\begin{Parallel}{.42\textwidth}{.42\textwidth}" + '\n')
    for i, inputLine in enumerate(chapter, start=1):
        emojiLine = inputLine[1]
        charList = splitEmojiLine(emojiLine)
        outputEmojiLineChars = []
        for e in charList:
            if re.match("^[_,;.:!?\"']$", e):
                e = PUNCTUATION_LATEXT_TABLE[e]
                outputEmojiLineChars.append(e)
            else:
                codePoint = '-'.join([str(hex(ord(c)))[2:] for c in e.decode('utf-8')])
                outputEmojiLineChars.append("\ie{" + codePoint + "}")
        outputEmojiLine = ' '.join(outputEmojiLineChars)
        outputEmojiLine = '\t' + r"\ParallelLText{" + outputEmojiLine + "}"

        #outputTextLineWords = inputLine[0]
        #outputTextLine = ' '.join(outputTextLineWords)
        outputTextLine = inputLine[0]
        outputTextLine = '\t' + r"\ParallelRText{" + outputTextLine + "}"

        lines.append(outputEmojiLine)
        lines.append(outputTextLine)

    lines.append('\n' + r"\end{Parallel}")
    return '\n'.join(lines)

def getLatexParcolPinocchioChapter(chapter_number):
    chapter = getPinocchioChapters()[chapter_number - 1]
    linesInChapter = len(chapter)
    lines = []
    for i, inputLine in enumerate(chapter, start=1):
        lines.append(r"\begin{paracol}[1]{2}")
        emojiLine = inputLine[1]
        charList = splitEmojiLine(emojiLine)
        outputEmojiLineChars = []
        for e in charList:
            if re.match("^[_,;.:!?\"']$", e):
                e = PUNCTUATION_LATEXT_TABLE[e]
                outputEmojiLineChars.append(e)
            else:
                codePoint = '-'.join([str(hex(ord(c)))[2:] for c in e.decode('utf-8')])
                outputEmojiLineChars.append("\ie{" + codePoint + "}")
        outputEmojiLine = ' '.join(outputEmojiLineChars)

        #outputTextLineWords = inputLine[0]
        #outputTextLine = ' '.join(outputTextLineWords)
        outputTextLine = inputLine[0]

        lines.append(r"\switchcolumn")
        lines.append(outputEmojiLine)
        lines.append(r"\switchcolumn")
        lines.append(outputTextLine)

        lines.append(r"\end{paracol}" + '\n')

    return '\n'.join(lines)

def checkPinocchioNormalizatin(chapter_number):
    exceptions = []
    chapter = getPinocchioChapters()[chapter_number-1]
    for l, line in enumerate(chapter, start=1):
        emojiLine = line[1]
        try:
            splitEmojiLine(emojiLine)
        except Exception as error:
            msg = str(error) + " in line " + str(l)
            exceptions.append(msg)
            if len(exceptions)==10:
                return '\n'.join(exceptions)
    if exceptions:
        return '\n'.join(exceptions)
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
    "✴️": "✴"
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
    #import emojiUtil
    if re.match("^[_,;.:!?\"']$",text):
        return [text]
    text = normalizeEmojisWithTable(text)
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
