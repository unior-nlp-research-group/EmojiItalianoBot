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

ASCII_PUNCTS = "_,;.:!?\"'()="
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
    "=": r'\eq',
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

#################
# PINOCCHIO BUILDING
#################

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
        spreadSheetTsv = r.content.split('\n')
        spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
        line_num = 1
        for row in spreadSheetReader:
            if len(row)<2:
                break
            words_sentence = row[0]
            emoji_sentence = convertPunctuation(row[1], ch_num, line_num)
            emojis_tokens = tokenize(emoji_sentence)
            emojis_tokens = fixPunctuationInGroups(emojis_tokens, ch_num, line_num)
            char_list, error = splitEmojiLineDebug(emojis_tokens)
            if error:
                print(error + " ch {} line {}".format(ch_num, line_num))
                break
            if len(row)>2 and utility.representsInt(row[2]):
                lines_in_paragraph = int(row[2])
            else:
                lines_in_paragraph = 0
                print("Missing lines in paragraph ch {} line {}".format(ch_num, line_num))
            clear_page = len(row) > 3 and row[3] == 'clear'
            sentence = (words_sentence, char_list, lines_in_paragraph, clear_page)
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

def convertPunctuation(text, ch_num=1, line_num=1):
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
    if underscore_was_opened:
        print "Uneven underscores in ch {} line {}".format(ch_num, line_num)
    if quotation_was_opened:
        print "Uneven quotation in ch {} line {}".format(ch_num, line_num)
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

# emoji_line_tokens must be a list of strings
# return a list of elements where each element is either
# - a punctuation
# - a single emoji
def splitEmojiLineDebug(emoji_line_tokens):
    import emojiUtil
    result = []
    error = ''
    for i, text_token in enumerate(emoji_line_tokens):
        if isPunctuation(text_token):
            parts = [text_token]
        else:
            parts = emojiUtil.splitEmojis(text_token)
        if parts:
            result.extend(parts)
        else:
            error = 'Problem in splitting {} ({}) in position {}/{}'.format(
                text_token, emojiUtil.getCodePointUpper(text_token), i, len(emoji_line_tokens))
    return result, error

#################
# FIND FUNCTIONS
#################


def findEmojiInPinocchio(inputEmojiText, deepSearch=False):
    PC = getPinocchioChapters()
    result = []
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter, 1):
            charList = row[1]
            emojiWords = getEmojiWords(charList)
            for ew in emojiWords:
                emojiWord = ''.join(ew)
                if inputEmojiText == emojiWord:
                    result.append("{0}.{1}".format(str(ch_num),str(line_num)))
                    break
                elif deepSearch:
                    line = ''.join(charList)
                    if line.find(inputEmojiText)>=0:
                        result.append("{0}.{1}".format(str(ch_num), str(line_num)))
                        break
    return result

def findTextInPinocchio(text):
    PC = getPinocchioChapters()
    result = []
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter, 1):
            line = row[0]
            if line.find(text) >= 0:
                result.append("{0}.{1}".format(str(ch_num), str(line_num)))
    return result

##########################
# READ PINOCCHIO FROM BOT
##########################

PINOCCHIO_EMOJI = '🏃'

def isValidChLineIndexStr(chLineIndex):
    ch_num, line_num = parseChLineIndex(chLineIndex)
    if ch_num is None:
        return None
    return isValidChLineIndex(ch_num, line_num)

def isValidChLineIndex(ch_num, line_num):
    PC = getPinocchioChapters()
    return ch_num>0 and ch_num<=len(PC) and line_num>0 and line_num<=len(PC[ch_num-1])

def parseChLineIndex(chLineIndex):
    import utility
    split = chLineIndex.split(':')
    if len(split) != 2:
        return None, None
    if not all([utility.representsInt(x) for x in split]):
        return None, None
    return [int(x) for x in split]

# idString is of type 1:1
def getSentenceEmojiString(chLineIndex):
    ch_num, line_num = parseChLineIndex(chLineIndex)
    if ch_num is None:
        return None
    PC = getPinocchioChapters()
    row = PC[ch_num-1][line_num-1]
    wordText = row[0]
    emojiTextGroup = getEmojiSpacingGroups(row[1])
    emojiText = ' '.join(''.join(g) for g in emojiTextGroup)
    header = "{}{}".format(PINOCCHIO_EMOJI, chLineIndex)
    return "{}\n\n{}\n\n{}".format(header, wordText, emojiText)

def getPrevChapterLineIndex(chLiIndex):
    ch_num, line_num = [int(x) for x in chLiIndex.split(':')]
    PC = getPinocchioChapters()
    if isValidChLineIndex(ch_num, line_num-1):
        return '{}:{}'.format(ch_num, line_num-1)
    if ch_num>1:
        return '{}:{}'.format(ch_num-1, len(PC[ch_num-2]))
    return None # beginning of book

def getNextChapterLineIndex(chLiIndex):
    ch_num, line_num = [int(x) for x in chLiIndex.split(':')]
    if isValidChLineIndex(ch_num, line_num + 1):
        return '{}:{}'.format(ch_num, line_num + 1)
    if isValidChLineIndex(ch_num+1, 1):
        return '{}:{}'.format(ch_num+1, 1)
    return None # end of book


#################
# EXPORT
#################

VERSION = '5'
BASE_DIR = "/Users/fedja/GDrive/Joint Projects/Emoji/Emojitaliano/Pinocchio/"
CHAPTER_TEXT_DIR = BASE_DIR + "/ChaptersText"
LATEX_DIR = BASE_DIR + "/EmojiPinocchioLatex/Prova{}".format(VERSION.zfill(2))
LATEX_DIR_CHECK = LATEX_DIR + '/check'

TAG_PASSATO = '◀'
TAG_FUTURO = '▶'
TAG_GERUNDIO_PART_PRESENTE_AVVERBIO = '⬅'
TAG_CAUSATIVO = '➡'
TAG_RIFLESSIVO = '👈'
TAG_RECIPROCO = '👥'
TAG_CONDIZIONALE = '🎲'
TAG_IMPERATIVO_ESORTATIVO = '❗'
TAG_DOPPIO_IMPERATIVO = '‼️'
TAG_IMPERATIVO_INTERROGATIVO = '⁉️'
TAG_INTERROGATIVO = '❓'
TAG_POSSESSIVO = '⏩'
TAG_DIMINUTIVO = '👶🏻'
TAG_DISPREGIATIVO = '👹'
TAG_SUPERLATIVO = '🔝'
FUNCTIONAL_TAGS = {TAG_PASSATO, TAG_FUTURO, TAG_GERUNDIO_PART_PRESENTE_AVVERBIO, TAG_CAUSATIVO,
                   TAG_RIFLESSIVO, TAG_RECIPROCO, TAG_CONDIZIONALE, TAG_IMPERATIVO_ESORTATIVO,
                   TAG_DOPPIO_IMPERATIVO, TAG_IMPERATIVO_INTERROGATIVO, TAG_INTERROGATIVO, TAG_POSSESSIVO,
                   TAG_DIMINUTIVO, TAG_DISPREGIATIVO, TAG_SUPERLATIVO}
FUNCTIONAL_TAGS_END = [TAG_PASSATO,TAG_FUTURO,TAG_GERUNDIO_PART_PRESENTE_AVVERBIO,TAG_RIFLESSIVO,TAG_RECIPROCO, TAG_DIMINUTIVO, TAG_DISPREGIATIVO, TAG_SUPERLATIVO]
FUNCTIONAL_TAGS_BEGINNING = [TAG_POSSESSIVO, TAG_CAUSATIVO,TAG_CONDIZIONALE, TAG_IMPERATIVO_ESORTATIVO, TAG_INTERROGATIVO]

def removeFunctionalTagsAndMakeSingular(emojiSequence):
    if len(emojiSequence)%2==0: #if even
        halfSize = len(emojiSequence) / 2
        if emojiSequence[:halfSize] == emojiSequence[halfSize:]: # if double emoji make singular
            emojiSequence = emojiSequence[:halfSize]
    while len(emojiSequence)>1 and emojiSequence[-1] in FUNCTIONAL_TAGS_END:
        emojiSequence = emojiSequence[:-1]
    while len(emojiSequence)>1 and emojiSequence[0] in FUNCTIONAL_TAGS_BEGINNING:
        emojiSequence = emojiSequence[1:]
    return emojiSequence

def testPinocchioEmojisAgainstDictionary(deleteGlossarioMissingInPinocchio=False):
    import gloss
    from collections import defaultdict
    PC = getPinocchioChapters()
    dictionaryGlosses = set(gloss.getAllGlossEmojis())
    pinocchioGlossesDict = defaultdict(list)
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter,1):
            charList = row[1]
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
    if deleteGlossarioMissingInPinocchio:
        from google.appengine.ext import ndb
        to_delete = []
        for e in missingInPinocchio:
            g = gloss.getGlossWithEmoji(e)
            assert g
            to_delete.append(g.key)
        print 'deleting {} glosses from dictionary not found in pinocchio'.format(len(to_delete))
        create_futures = ndb.delete_multi_async(to_delete)
        ndb.Future.wait_all(create_futures)
    pinocchioGlossesIndexes = ['{}: {}'.format(e, ', '.join(iList)) for e, iList, in pinocchioGlossesDict.iteritems()]
    missingInDictionaryFile = LATEX_DIR_CHECK + '/MissingInDictionary.txt'
    missingInPinocchioFile = LATEX_DIR_CHECK + '/MissingInPinocchio.txt'
    pinocchioFile = LATEX_DIR_CHECK + '/PinocchioGlosses.txt'
    dictionaryFile = LATEX_DIR_CHECK + '/DictionaryGlosses.txt'
    for file, emojiList in zip(
            [missingInDictionaryFile, missingInPinocchioFile, pinocchioFile, dictionaryFile],
            [missingInDictionaryIndexes, missingInPinocchio, pinocchioGlossesIndexes, dictionaryGlosses]):
        with open(file, 'w') as f:
            for e in emojiList:
                f.write('{}\n'.format(e))
            f.close()

def checkPinocchioTranslation():
    emoji_singoli_list = []
    search_tags = {}
    uneven_under_open_close_list = []
    for t in FUNCTIONAL_TAGS:
        search_tags[t] = []
    PC = getPinocchioChapters()
    for ch_num, chapter in enumerate(PC, 1):
        for line_num, row in enumerate(chapter,1):
            charList = row[1]
            if hasUnevenUnderOpenClose(charList):
                uneven_under_open_close_list.append('{}.{}'.format(ch_num, line_num))
            cornici_groups = getCornici(charList)
            for cg in cornici_groups:
                if len(cg)==1:
                    emoji_singoli_list.append('{}.{} → {}'.format(ch_num, line_num, cg[0]))
            emojiWords = getEmojiWords(charList)
            for ew in emojiWords:
                for t,l in search_tags.items():
                    if t in ew:
                        l.append('{}.{} → {}'.format(ch_num, line_num, ''.join(ew)))

    if uneven_under_open_close_list:
        print 'Problema in cornici non chiuse correttamente: {}'.format(', '.join(uneven_under_open_close_list))
        return

    out_file = LATEX_DIR_CHECK + '/checkPinocchioTranslation.txt'
    with open(out_file, 'w') as f:
        for t, l in search_tags.items():
            f.write('paragrafi con {}: {}'.format(t, ', '.join(l)))
            f.write('\n\n')
        f.write('paragrafi con emoji singoli in cornici: {}'.format(', '.join(emoji_singoli_list)))
        f.close()

def checkPinocchioGlossario():
    import gloss
    import emojiUtil
    search_tags = {}
    for t in FUNCTIONAL_TAGS:
        search_tags[t] = []
    emojiGloss = gloss.getAllGlossEmojis()
    for eg in emojiGloss:
        parts = emojiUtil.splitEmojis(eg)
        for t, l in search_tags.items():
            if t in parts:
                l.append(eg)
    out_file = LATEX_DIR_CHECK + '/checkPinocchioGlossario.txt'
    with open(out_file, 'w') as f:
        for t, l in search_tags.items():
            f.write('glosses con {}: {}'.format(t, ', '.join(l)))
            f.write('\n\n')
        f.close()


def hasUnevenUnderOpenClose(charList):
    inside = False
    for ch in charList:
        if ch == UNDER_OPEN:
            if inside:
                return True
            inside = not inside
        elif ch == UNDER_CLOSE:
            if not inside:
                return True
            inside = not inside
    if inside:
        return True
    return False

def saveTextChapters():
    for i in range(len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
        chapter_number = i+1
        outputFile = CHAPTER_TEXT_DIR + "/Pinocchio_ch{}.txt".format(str(chapter_number).zfill(2))
        with open(outputFile, 'w') as f:
            chapter = getPinocchioChapters()[chapter_number - 1]
            for row in chapter:
                charList = row[1]
                charGroups = getEmojiSpacingGroups(charList)
                line = ' '.join(''.join(g) for g in charGroups)
                f.write("{}\n".format(line))
            f.close()

def saveLatexChapters():
    for i in range(len(PINOCCHIO_CHAPTERS_DOC_KEYS)):
        chapter_number = i+1
        outputFile = LATEX_DIR + "/Pinocchio_ch{}.txt".format(str(chapter_number).zfill(2))
        getLatexPinocchioChapter(chapter_number, outputFile)

def saveLatexDictionary():
    import gloss
    import emojiUtil
    outputFile = LATEX_DIR + "/dictionary_entries.txt"
    source_targets = gloss.getAllGlossSourceTarget()
    source_targets.sort(key=lambda x:x[0])
    with open(outputFile, 'w') as f:
        for st in source_targets:
            emoji_parts = emojiUtil.splitEmojis(st[0])
            outputEmojiLineCmds = []
            #'''
            for i, ch in enumerate(emoji_parts):
                if i > 0:  # no space before first char in group
                    outputEmojiLineCmds.append(SPACE_SMALL)
                codePoint = '-'.join([str(hex(ord(c)))[2:] for c in ch.decode('utf-8')])
                outputEmojiLineCmds.append("\\ie{" + codePoint + "}")
            f.write("\entry{{{}}}{{{}}}.\n\n".format(' '.join(outputEmojiLineCmds), ', '.join(st[1])))
            #'''
            #f.write("\entry{{{}}}{{{}}}\n".format(st[0], ', '.join(st[1])))
        f.close()

def mergePdf():
    from pyPdf import PdfFileReader, PdfFileWriter
    textCompletePdf = LATEX_DIR + "/Pinocchio_TestoCompleto.pdf"
    #emojiCompletePdf = LATEX_DIR + "/Pinocchio_EmojiCompleto.pdf"
    emojiCompletePdf = LATEX_DIR + "/latex_chapters.pdf"
    mergedCompletePdf = LATEX_DIR + "/Pinocchio_MergedCompleto.pdf"

    output = PdfFileWriter()
    input1 = PdfFileReader(file(textCompletePdf, "rb"))
    input2 = PdfFileReader(file(emojiCompletePdf, "rb"))

    for p in range(56):
        page1 = input1.getPage(p)
        page2 = input2.getPage(p)
        page1.mergePage(page2)
        output.addPage(page1)

    outputStream = file(mergedCompletePdf, "wb")
    output.write(outputStream)
    outputStream.close()

def saveLatexGrammar():
    import utility
    import grammar_rules
    outputFile = LATEX_DIR + "/Pinocchio_grammar.txt"
    with open(outputFile, 'w') as f:
        GS = grammar_rules.getGrammarStructure()
        line_num = 0
        for title in grammar_rules.RULE_TYPES_SORTED:
            f.write("\n\n" + "\\section{" + title + "}\n\n")
            f.write("\\begin{enumerate}\n")
            title_rules = GS[title]['rules']
            for rule in title_rules:
                f.write("\\item ")
                line_num += 1
                rule_tokens = rule.split()
                for token in rule_tokens:
                    if utility.containsAlpha(token):
                        f.write("{} ".format(token))
                    else:
                        for p in ["'", UNDER_OPEN, UNDER_CLOSE]:
                            token = token.replace(p, ' {} '.format(p))
                        emoji_parts = tokenize(token)
                        char_list, error = splitEmojiLineDebug(emoji_parts)
                        if error:
                            print('{} at line {}'.format(error, line_num))
                            return
                        outputEmojiLineCmds = []
                        for i, ch in enumerate(char_list):
                            if i > 0:  # no space before first char in group
                                if isPunctuation(ch) and ch != UNDER_CLOSE:  # and previous not in [UNDER_OPEN]:
                                    outputEmojiLineCmds.append(SPACE_MEDIUM)
                                else:
                                    outputEmojiLineCmds.append(SPACE_SMALL)
                            if isPunctuation(ch):
                                outputEmojiLineCmds.append(PUNCTUATION_LATEXT_TABLE[ch])
                            else:
                                codePoint = '-'.join([str(hex(ord(c)))[2:] for c in ch.decode('utf-8')])
                                outputEmojiLineCmds.append("\\ie{" + codePoint + "}")
                        f.write("\\RemoveSpaces{" + ' '.join(outputEmojiLineCmds) + "} ") # remove auto spacing
            f.write("\\end{enumerate}\n\n")
        f.close()

def getLatexPinocchioChapter(chapter_number, outputFile):
    chapter = getPinocchioChapters()[chapter_number - 1]
    lines = []
    use_frames = False
    for row in chapter:
        charList = row[1]
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
            clear_page = chapter[i][3]
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
            if clear_page:
                f.write('\\clearpage' + '\n\n')
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

def getCornici(charList):
    groups = []
    current_cornice = []
    inside_cornice = False
    for ch in charList:
        if ch in [UNDER_OPEN, UNDER_CLOSE]:
            inside_cornice = not inside_cornice
            if current_cornice and ch==UNDER_CLOSE:
                groups.append(current_cornice)
                current_cornice = []
        elif inside_cornice:
            current_cornice.append(ch)
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

