# -*- coding: utf-8 -*-

import re

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

ASCII_PUNCTS = "_,;.:!?\"'"
PUNCT_RE_MATCH = "^[{}]$".format(ASCII_PUNCTS)
TOKEN_RE_SPLIT = "([\s{}])".format(ASCII_PUNCTS)
UNDER_OPEN = '⌊'
UNDER_CLOSE = '⌋'
QUOTE_OPEN = '“'
QUOTE_CLOSE = '”'
THREE_DOTS = "…"
QUOTE_OPEN_VAR = '«'
QUOTE_CLOSE_VAR = '»'
NON_ASCII_PUNCTS = [UNDER_OPEN, UNDER_CLOSE, QUOTE_OPEN, QUOTE_CLOSE, THREE_DOTS, QUOTE_OPEN_VAR, QUOTE_CLOSE_VAR]

def isPunctuation(ch):
    return re.match(PUNCT_RE_MATCH, ch) or ch in NON_ASCII_PUNCTS



PUNCTUATION_LATEXT_TABLE = {
    "_": r'\under',
    "'": r'\sq',
    '"': r'\dq',
    "-": r'\dash',
    ".": r'\period',
    ":": r'\colonpunct',
    ",": r'\comma',
    ";": r'\semicolon',
    "!": r'\excl',
    "?": r'\quest',
    "(": r'\opar',
    ")": r'\cpar',
    UNDER_OPEN: r'\underOpen',
    UNDER_CLOSE: r'\underClose',
    THREE_DOTS: r'\threeDots',
    QUOTE_OPEN: r'\quoteOpen',
    QUOTE_CLOSE: r'\quoteClose',
    QUOTE_OPEN_VAR: r'\quoteVarOpen',
    QUOTE_CLOSE_VAR: r'\quoteVarClose'
}

SPACE_SMALL = r'\sSp'
SPACE_MEDIUM = r'\mSp'
SPACE_BIG = r'\bSp'

PINOCCHIO_CHAPTERS = None

def getPinocchioChapters():
    global PINOCCHIO_CHAPTERS
    if PINOCCHIO_CHAPTERS==None:
        buildPinocchioChapters()
    return PINOCCHIO_CHAPTERS

def buildPinocchioChapters():
    import csv, requests, utility
    global PINOCCHIO_CHAPTERS
    PINOCCHIO_CHAPTERS = []
    for ch_num, ch_key in enumerate(PINOCCHIO_CHAPTERS_DOC_KEYS, 1):
        chapterSentences = []
        url = PINOCCHIO_CHAPTER_URL.format(ch_key)
        r = requests.get(url)
        spreadSheetTsv = r.iter_lines()
        spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
        line_num = 1
        for row in spreadSheetReader:
            if len(row)<2:
                break
            words_sentence = row[0]
            emoji_sentence = convertPunctuation(row[1])
            emojis_tokens = tokenize(emoji_sentence)
            emojis_tokens = fixPunctuationInGroups(emojis_tokens, ch_num, line_num)
            lines_in_paragraph = int(row[2]) if len(row)>2 and utility.representsInt(row[2]) else -1
            sentence = (words_sentence, emojis_tokens, lines_in_paragraph)
            chapterSentences.append(sentence)
            line_num += 1
        PINOCCHIO_CHAPTERS.append(chapterSentences)

def formatEmojiText(emojiText):
    emoji_sentence = convertPunctuation(emojiText)
    emojis_tokens = tokenize(emoji_sentence)
    emojis_tokens = fixPunctuationInGroups(emojis_tokens)
    groups = getEmojiSpacingGroups(emojis_tokens)
    return ' '.join([''.join(g) for g in groups])

def getPinocchioEmojiChapterSentence(chapter, sentence):
    return getPinocchioChapters()[chapter-1][sentence-1][1]

def convertPunctuation(text):
    text = text.replace('...', THREE_DOTS)
    for p in NON_ASCII_PUNCTS:
        text = text.replace(p, ' {} '.format(p))
    newChars = []
    underscore_was_opened, quotation_was_opened = False, False
    for ch in text:
        if isPunctuation(ch):
            if ch == '_':
                ch = UNDER_OPEN if not underscore_was_opened else UNDER_CLOSE
                underscore_was_opened = not underscore_was_opened
            elif ch == '"':
                ch = QUOTE_OPEN if not quotation_was_opened else QUOTE_CLOSE
                quotation_was_opened = not quotation_was_opened
            ch = ' {} '.format(ch)
        newChars.append(ch)
    return ''.join(newChars)

# separate emoji from punctuation
def tokenize(emoji_line):
    tokens = [x.strip() for x in re.split(TOKEN_RE_SPLIT, emoji_line.strip()) if
              x.strip() != '' and x.strip() != ' ']
    return tokens

def fixPunctuationInGroups(tokens, ch_num=1, line_num=1):
    debug = True
    new_tokens = []
    inside_concatenation = False
    last_under_open_index = -1
    current_group = []
    for i, t in enumerate(tokens):
        if t == UNDER_OPEN:
            current_group = []
            last_under_open_index = i
        current_group.append(t)
        if t == "'" and inside_concatenation:
            new_tokens.insert(last_under_open_index, "'")
        else:
            new_tokens.append(t)
        if debug and inside_concatenation and t != "'" and t not in [UNDER_OPEN, UNDER_CLOSE] and isPunctuation(t):
            print "{}.{} - Punctuation in group: {}".format(ch_num, line_num, ' '.join(current_group))
        if t in [UNDER_OPEN, UNDER_CLOSE]:
            inside_concatenation = not inside_concatenation
    return new_tokens

def findEmojiInPinocchio(inputEmojiText, deepSearch=False):
    PC = getPinocchioChapters()
    result = []
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter, 1):
            emojiLineTokens = row[1]
            charList = splitEmojiLineDebug(emojiLineTokens)
            emojiWords = getEmojiWords(charList)
            for ew in emojiWords:
                emojiWord = ''.join(ew)
                if inputEmojiText == emojiWord:
                    result.append("{0}.{1}".format(str(ch_num),str(line_num)))
                    break
                elif deepSearch:
                    line = ''.join(emojiLineTokens)
                    if line.find(inputEmojiText)>=0:
                        result.append("{0}.{1}".format(str(ch_num), str(line_num)))
                        break
    return result

# return a list of elements where each element is either
# - a punctuation
# - a single emoji
def splitEmojiLineDebug(emoji_line_tokens):
    import emojiUtil
    result = []
    for i, text_token in enumerate(emoji_line_tokens):
        if isPunctuation(text_token):
            parts = [text_token]
        else:
            parts = emojiUtil.splitEmojis(text_token)
        if parts:
            result.extend(parts)
        else:
            raise Exception('Problem in splitting {} ({}) in position {}/{}'.format(
                text_token, emojiUtil.getCodePointStr(text_token), i, len(emoji_line_tokens)))
    return result

#################
# EXPORT
#################

VERSION = '5'
LATEX_DIR = "/Users/fedja/GDrive/Joint Projects/Emoji/Emojitaliano/" \
                "Pinocchio/EmojiPinocchioLatex/Prova{}".format(VERSION.zfill(2))


TAG_PASSATO = '◀'
TAG_FUTURO = '▶'
TAG_GERUNDIO_PART_PRESENTE_AVVERBIO = '⬅'
TAG_CAUSATIVO = '➡'
TAG_RIFLESSIVO = '👈'
TAG_RECIPROCO = '👥'
TAG_CONDIZIONALE = '🎲'
TAG_IMPERATIVO_ESORTATIVO = '❗'
TAG_INTERROGATIVO = '❓'
FUNCTIONAL_TAGS_END = [TAG_PASSATO,TAG_FUTURO,TAG_GERUNDIO_PART_PRESENTE_AVVERBIO,TAG_CAUSATIVO,TAG_RIFLESSIVO,TAG_RECIPROCO]
FUNCTIONAL_TAGS_BEGINNING = [TAG_CONDIZIONALE, TAG_IMPERATIVO_ESORTATIVO, TAG_INTERROGATIVO]

def removeFunctionalTagsAndMakeSingular(emojiSequence):
    while len(emojiSequence)>1 and emojiSequence[-1] in FUNCTIONAL_TAGS_END:
        emojiSequence = emojiSequence[:-1]
    while len(emojiSequence)>1 and emojiSequence[0] in FUNCTIONAL_TAGS_BEGINNING:
        emojiSequence = emojiSequence[1:]
    if len(emojiSequence)%2==0: #if even
        halfSize = len(emojiSequence) / 2
        if emojiSequence[:halfSize] == emojiSequence[halfSize:]: # ifdouble emoji make singular
            emojiSequence = emojiSequence[:halfSize]
    return emojiSequence

def testPinocchioEmojisAgainstDictionary():
    import gloss
    from collections import defaultdict
    PC = getPinocchioChapters()
    dictionaryGlosses = set(gloss.getAllGlossEmojis())
    pinocchioGlossesDict = defaultdict(list)
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter,1):
            emojiLineTokens = row[1]
            charList = splitEmojiLineDebug(emojiLineTokens)
            emojiWords = getEmojiWords(charList)
            for ew in emojiWords:
                emojiGloss = ''.join(ew)
                if emojiGloss not in dictionaryGlosses:
                    ew = removeFunctionalTagsAndMakeSingular(ew)
                    emojiGloss = ''.join(ew)
                pinocchioGlossesDict[emojiGloss].append('{}.{}'.format(ch_num, line_num))
    pinocchioGlosses = set(pinocchioGlossesDict.keys())
    missingInDictionary = set(pinocchioGlosses).difference(dictionaryGlosses)
    missingInDictionaryIndexes = ['{}: {}'.format(e, ', '.join(pinocchioGlossesDict[e])) for e in missingInDictionary]
    missingInPinocchio = set(dictionaryGlosses).difference(pinocchioGlosses)
    pinocchioGlossesIndexes = ['{}: {}'.format(e, ', '.join(iList)) for e, iList, in pinocchioGlossesDict.iteritems()]
    missingInDictionaryFile = LATEX_DIR + '/check_MissingInDictionary.txt'
    missingInPinocchioFile = LATEX_DIR + '/check_MissingInPinocchio.txt'
    pinocchioFile = LATEX_DIR + '/check_PinocchioGlosses.txt'
    dictionaryFile = LATEX_DIR + '/check_DictionaryGlosses.txt'
    for file, emojiList in zip(
            [missingInDictionaryFile, missingInPinocchioFile, pinocchioFile, dictionaryFile],
            [missingInDictionaryIndexes, missingInPinocchio, pinocchioGlossesIndexes, dictionaryGlosses]):
        with open(file, 'w') as f:
            for e in emojiList:
                f.write('{}\n'.format(e))
            f.close()


def mergePdf():
    from pyPdf import PdfFileReader, PdfFileWriter
    textCompletePdf = LATEX_DIR + "/Pinocchio_TestoCompleto.pdf"
    #emojiCompletePdf = LATEX_DIR + "/Pinocchio_EmojiCompleto.pdf"
    emojiCompletePdf = LATEX_DIR + "/main.pdf"
    mergedCompletePdf = LATEX_DIR + "/Pinocchio_MergedCompleto.pdf"

    output = PdfFileWriter()
    input1 = PdfFileReader(file(textCompletePdf, "rb"))
    input2 = PdfFileReader(file(emojiCompletePdf, "rb"))

    for p in range(3):
        page1 = input1.getPage(p)
        page2 = input2.getPage(p)
        page1.mergePage(page2)
        output.addPage(page1)

    outputStream = file(mergedCompletePdf, "wb")
    output.write(outputStream)
    outputStream.close()


def saveLatexChapters():
    for i in range(len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
        chapter_number = i+1
        outputFile = LATEX_DIR + "/Pinocchio_ch{}.txt".format(str(chapter_number).zfill(2))
        getLatexPinocchioChapter(chapter_number, outputFile)

def getLatexPinocchioChapter(chapter_number, outputFile):
    chapter = getPinocchioChapters()[chapter_number - 1]
    lines = []
    use_frames = False
    for row in chapter:
        emojiLineTokens = row[1]
        charList = splitEmojiLineDebug(emojiLineTokens)
        charGroups = getEmojiSpacingGroups(charList)
        outputEmojiLineCmds = []
        for g, charsInGroup in enumerate(charGroups):
            useConcatenation = len(charsInGroup) > 1
            if useConcatenation:
                # beginning of concatenation
                outputEmojiLineCmds.append('\\mbox{') #replace with fbox if you want to see the concatenations
            for i, ch in enumerate(charsInGroup):
                if isPunctuation(ch):
                    symbol = PUNCTUATION_LATEXT_TABLE[ch]
                else:
                    codePoint = '-'.join([str(hex(ord(c)))[2:] for c in ch.decode('utf-8')])
                    symbol = "\\ie{" + codePoint + "}"
                if use_frames:
                    symbol = "\\fbox{" + symbol + "}"
                # compute space
                if i>0: #no space before first char in group
                    if isPunctuation(ch) and ch != UNDER_CLOSE: #and previous not in [UNDER_OPEN]:
                        outputEmojiLineCmds.append(SPACE_MEDIUM)
                    else:
                        outputEmojiLineCmds.append(SPACE_SMALL)
                outputEmojiLineCmds.append(symbol)
            if useConcatenation:
                # end of concatenation
                outputEmojiLineCmds.append('}')
            if g!=len(charGroups)-1:
                outputEmojiLineCmds.append(SPACE_BIG)
        outputEmojiLine = ' '.join(outputEmojiLineCmds)
        lines.append(outputEmojiLine)

    with open(outputFile, 'w') as f:
        for i, l in enumerate(lines):
            lines_in_paragraph = chapter[i][2]
            f.write("%{}\n".format(i)) # line number in comment
            l = "\\RemoveSpaces{\n" + l + "\n}" # remove auto spacing
            if i ==0:
                # chapter number
                height = lines_in_paragraph * 13.6 + 7.0
                l = "\\begin{center}\n" + "\\scalebox{1.5}{\n" + l + "\n}" + "\n\\end{center}"
            elif i == 1:
                # chapter title
                #l = "\\begin{center}\n" + "\\scalebox{0.8}{\n" + l + "\n}" + "\n\\end{center}"
                l = "\\begin{center}\n" + l + "\n\\end{center}"
                height = lines_in_paragraph * 12.0 + 20
            else:
                height = lines_in_paragraph * 13.6
            f.write("\\begin{minipage}" + "[t][{}pt][t]".format(height) + "{\\textwidth}\n" + l + "\n\\end{minipage}")
            f.write('\n\n')
        f.close()

# returns a list of emoji groups according to the concatenation symbols
# each group is a list of signle emoji and single punctuation symbols
# the puntuation is incorporated to the previous/next group
# depending on the type of puntuation (so not to leave it isolated incorrectly).
def getEmojiSpacingGroups(charList):
    groups = []
    current_group = []
    inside_concatenation = False
    previous = ''
    for ch in charList:
        if current_group and previous not in [QUOTE_OPEN, "'"] and not inside_concatenation and \
                (ch in ["'", UNDER_OPEN] or not isPunctuation(ch)):
            # start new group
            groups.append(current_group)
            current_group = []
        if ch in [UNDER_OPEN, UNDER_CLOSE]:
            inside_concatenation = not inside_concatenation
        current_group.append(ch)
        previous = ch
    if current_group:
        groups.append(current_group)
    return groups

def getEmojiWords(charList):
    groups = []
    current_group = []
    inside_concatenation = False
    for ch in charList:
        if current_group and not inside_concatenation:
            # start new group
            groups.append(current_group)
            current_group = []
        if ch in [UNDER_OPEN, UNDER_CLOSE]:
            inside_concatenation = not inside_concatenation
        if not isPunctuation(ch):
            current_group.append(ch)
    if current_group:
        groups.append(current_group)
    return groups


#################
# CHECK FUNCTIONS
#################

def fullCheckPinocchio():
    for i in range(len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
        chapter_number = i+1
        error_types = {
            'Normalization Errors': checkPinocchioNormalizationChapter(chapter_number),
            'Line Counts Errors': checkLinesParagraphChapter(chapter_number),
            'Underscores Errors': checkOpenCloseSymbolChapter(chapter_number, '_'),
            'Quotations Errors': checkOpenCloseSymbolChapter(chapter_number, '"'),
        }
        errors = any(len(e)>0 for e in error_types.values())
        if errors:
            print "ch {}: ERRORS!".format(chapter_number)
            for error_title, errors in error_types.iteritems():
                if errors:
                    print '\t{}'.format(error_title)
                    for e in errors:
                        print '\t\t- {}'.format(e)
        if not errors:
            print "ch {}: All OK!".format(chapter_number)


def checkPinocchioNormalizationChapter(chapter_number):
    errors = []
    chapter = getPinocchioChapters()[chapter_number-1]
    for i, row in enumerate(chapter, start=1):
        emojiLineTokens = row[1]
        try:
            splitEmojiLineDebug(emojiLineTokens)
        except Exception as error:
            msg = str(error) + " line {}".format(chapter_number, i)
            errors.append(msg)
            #if len(exceptions)==10:
            #    return '\n'.join(exceptions)
    return errors

def checkLinesParagraphChapter(chapter_number):
    error_lines = []
    chapter = getPinocchioChapters()[chapter_number - 1]
    for i, row in enumerate(chapter, start=1):
        line_count = row[2]
        if line_count==-1:
            error_lines.append('Wrong field in line: {}'.format(i))
    return error_lines

def checkOpenCloseSymbolChapter(chapter_number, symbol):
    errors = []
    chapter = getPinocchioChapters()[chapter_number - 1]
    for i, row in enumerate(chapter, start=1):
        emojiLine = row[1]
        symbol_was_opened = False
        for e in emojiLine: #charList
            if e == symbol:
                symbol_was_opened = not symbol_was_opened
        if symbol_was_opened:
            errors.append("Error at row {}".format(i))
    return errors

'''

EMOJI_NORMALIZATION_TABLE = {
    "◀️": "◀",
    "▶️": "▶",
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
    "‼️": "‼",
    "❗️": "❗",
    "⁉️": "⁉",
    "✔️": "✔",
    "♒️": "♒",
    "⚠️": "⚠",
    "🍒️": "🍒",
    "⚡️": "⚡",
    "✴️": "✴",
    "❄️": "❄",
    "♻️": "♻",
    "♊️": "♊",
    "🅰️": "🅰",
    "〽️": "〽",
    "☁️": "☁",
    "☹️": "☹",
    "✂️": "✂",
    "🏃️": "🏃",
    "⌛️": "⌛",
    "☝️": "☝",
    "✌️": "✌",
    "✋️": "✋",
    "⛳️": "⛳",
    "⛔️": "⛔",
    "⚔️": "⚔",
    "☮️": "☮",
    "⚫️": "⚫",
    "⚪️": "⚪",
    "⬜️": "⬜",
    "✈️": "✈"
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

def checkSmartNormalization():
    uni_emptySymbol = u'\ufe0f'
    for k,v in EMOJI_NORMALIZATION_TABLE.iteritems():
        uni_k = k.decode('utf-8')
        uni_v = v.decode('utf-8')
        if len(uni_k)==2 and uni_k[0]==uni_v and uni_k[1]==uni_emptySymbol:
            print "Norm {}  OK!".format(k)
        else:
            print "Norm {}  PROBLEM: k={}   v={}!".format(k, getCoidePointStr(k), getCoidePointStr(v))


def checkNormalizationTable():
    for old,new in EMOJI_NORMALIZATION_TABLE.iteritems():
        old_is_emoji = old.decode('utf-8') in emoji_tables.ALL_EMOJIS
        new_is_emoji = new.decode('utf-8') in emoji_tables.ALL_EMOJIS
        if old_is_emoji or not new_is_emoji:
            print '{} - {} ({} - {}) {} {}'.format(old, new, getCoidePointStr(old), getCoidePointStr(new), old_is_emoji, new_is_emoji)


'''