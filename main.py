# -*- coding: utf-8 -*-

import json
import logging
import urllib
import urllib2
import person
from person import Person
from datetime import timedelta
from time import sleep

import key
import gloss

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.ext.db import datastore_errors

import webapp2
from random import randint
import confusionTables
import emojiUtil
import utility
import unicodedata
import string
import pinocchio
import grammar_rules
import futuroRemoto

from jinja2 import Environment, FileSystemLoader

# ================================
# ================================
# ================================

WORK_IN_PROGRESS = False

# ================================
# ================================
# ================================


BASE_URL = 'https://api.telegram.org/bot' + key.TOKEN + '/'
BASE_URL_FILE = 'https://api.telegram.org/bot/file/bot' + key.TOKEN + '/'

DASHBOARD_DIR_ENV = Environment(loader=FileSystemLoader('dashboard'), autoescape = True)

ISTRUZIONI =  \
"""
@emojitalianobot è un tool gratuito e aperto alla comunità per costruire un dizionario italiano degli emoji.
Attualmente hai la possibilità di cercare parole o emoji o giocare per indovinare le traduzioni.

Se hai bisogno di aiuto o vuoi aiutarci a migliorare il bot vieni nel gruppo di discussione cliccando su
telegram.me/joinchat/B8zsMQg_NUYAROsKeUe8Xw

In @emojitalianobot anche il glossario  di Pinocchio in emojitaliano:
scritturebrevi.it/2016/02/05/pinocchio-in-emojitaliano-the-emoji-column

Aiutaci a far conoscere questo bot invitando altri amici e votandolo su
telegramitalia.it/emojitalianobot e su telegram.me/storebot?start=emojitalianobot

Per maggiori informazioni visita scritturebrevi.it/emojitalianobot

@emojitalianobot v.6
"""

INVITE_FRIEND_INSTRUCTION = \
"""
Per invitare un amico, copia il messaggio seguente 🗒 e incollalo in un'altra chat, o inoltralo ⏩ direttamente \
(per istruzioni premi su /comeInoltrareUnMessaggio):
"""

MESSAGE_FOR_FRIENDS = \
"""
Ciao, ho scoperto @emojitalianobot, un *tool gratuito e aperto alla comunità* per creare un *dizionario italiano degli emoji*.
Penso che ti piacerà 😍!
Basta premere su @emojitalianobot e fare *START*!
"""

HOW_TO_FORWARD_A_MESSAGE = \
"""
Come *inoltrare un messaggio* in Telegram in due semplici passaggi:

1 (Browser): click (sinistro) sul messaggio e premi 'inoltra' in basso
1 (Desktop): click (destro) sull'orario vicino al messaggio e seleziona 'inoltra'
1 (SmartPhone): tieni premuto su un messaggio e seleziona l'icona di inoltro

2: seleziona l'utente a cui vuoi mandare il messaggio

"""



STATES = {
    0: 'Initial Screen',
    20: 'IT <-> EMOJI',
    21: 'EN <-> EMOJI',
    30: 'PINOCCHIO',
    40: 'GLOSSARIO PINOCCHIO',
    41: 'GLOSSARIO: INSERISCI VOCE',
    42: 'GLOSSARIO: ELIMINA VOCE',
    50: 'GAME PANEL',
    51: 'GAME PANEL -> word to emoji',
    52: 'GAME PANEL -> emoji to word',
    60: 'GRAMMATICA PINOCCHIO',
    80: 'FuturoRemoto'
}

CANCEL = u'\U0000274C'.encode('utf-8')
CHECK = u'\U00002705'.encode('utf-8')

THUMB = b'\xF0\x9F\x91\x8D'
FOOTPRINTS = b'\xF0\x9F\x91\xA3'
NOENTRY = b'\xF0\x9F\x9A\xAB'
CLAPPING_HANDS = b'\xF0\x9F\x91\x8F'
SMILING_FACE = b'\xF0\x9F\x98\x8A'
GEAR = b'\xE2\x9A\x99'
LEFTWARDS_BLACK_ARROW = b'\xE2\xAC\x85'
BLACK_RIGHTWARDS_ARROW = b'\xE2\x9E\xA1'
LETTERS = u'\U0001F520'.encode('utf-8')
SMILY = u'\U0001F60A'.encode('utf-8')
RIGHT_ARROW = u'\U000027A1'.encode('utf-8')

IT_FLAG = u'\U0001F1EE\U0001F1F9'.encode('utf-8')
EN_FLAG = u'\U0001F1EC\U0001F1E7'.encode('utf-8')


IT_TO_EMOJI = IT_FLAG + ' ' + RIGHT_ARROW + ' ' + SMILY
EMOJI_TO_IT = SMILY + ' ' + RIGHT_ARROW + ' ' + IT_FLAG
EN_TO_EMOJI = EN_FLAG + ' ' + RIGHT_ARROW + ' ' + SMILY
EMOJI_TO_EN = SMILY + ' ' + RIGHT_ARROW + ' ' + EN_FLAG

IT_TEXT_TOFROM_EMOJI = '🇮🇹🔠 ↔ 😊'
EN_TEXT_TOFROM_EMOJI = '🇬🇧🔠 ↔ 😊'

CAPIRE = u'\U0001F4A1'.encode('utf-8')
LEGGERE = u'\U0001F440'.encode('utf-8') + u'\U0001F4D6'.encode('utf-8')
BOOK = u'\U0001F4D6'.encode('utf-8')
PINOCCHIO = u'\U0001F3C3'.encode('utf-8')
SOS = u'\U0001F198'.encode('utf-8')
INFO = u'\U00002139'.encode('utf-8')
JOKER = u'\U0001F0CF'.encode('utf-8')
MASCHERE = u'\U0001F3AD'.encode('utf-8')
WARNING_SIGN = u'\U000026A0'.encode('utf-8')
EXCLAMATION = u'\U00002757'.encode('utf-8')
UNDER_CONSTRUCTION = u'\U0001F6A7'.encode('utf-8')
FROWNING_FACE = u'\U0001F641'.encode('utf-8')

BOTTONE_ANNULLA = CANCEL + " Annulla"
BOTTONE_INDIETRO = LEFTWARDS_BLACK_ARROW + ' ' + "Indietro"
BOTTONE_PINOCCHIO = PINOCCHIO + ' PINOCCHIO'
BOTTONE_GLOSSARIO = PINOCCHIO + ' GLOSSARIO'
BOTTONE_GRAMMATICA = PINOCCHIO + ' GRAMMATICA'
BOTTONE_INFO = INFO + ' INFO'
BOTTONE_GIOCA = JOKER + ' GIOCA!'
BOTTONE_INVITA_AMICO = MASCHERE + ' INVITA UN AMICO'
BOTTONE_SI = CHECK + ' SI'
BOTTONE_NO = CANCEL + ' NO'

FUTURO_REMOTO_COMMAND = "futuroremoto"
# ================================
# AUXILIARY FUNCTIONS
# ================================


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2)+1):
        yield chr(c)

latin_letters= {}

def is_latin(uchr):
    try: return latin_letters[uchr]
    except KeyError:
         return latin_letters.setdefault(uchr, 'LATIN' in unicodedata.name(uchr))

def only_roman_chars(unistr):
    return all(is_latin(uchr)
           for uchr in unistr
           if uchr.isalpha()) # isalpha suggested by John Machin

def remove_accents_roman_chars(text):
    text_uni = text.decode('utf-8')
    if not only_roman_chars(text_uni):
        return text
    msg = ''.join(x for x in unicodedata.normalize('NFKD', text_uni) if (x==' ' or x in string.ascii_letters))
    return msg.encode('utf-8')

def normalizeString(text):
    return remove_accents_roman_chars(text.lower()).lower()

def has_roman_chars(text):
    textNorm = normalizeString(text)
    return any(x in string.ascii_letters for x in textNorm)

# ================================
# ================================
# ================================

def restartAllUsers(msg):
    qry = Person.query()
    count = 0
    for p in qry:
        if (p.enabled): # or p.state>-1
            if msg:
                sleep(0.100)  # no more than 10 messages per second
                tell(p.chat_id, msg)
            restart(p)
    logging.debug("Succeffully restarted users: " + str(count))
    return count

def restartTest(msg):
    qry = Person.query(Person.chat_id==key.PINCO_PALLINO_CHAT_ID)
    count = 0
    for p in qry:
        if (p.enabled): # or p.state>-1
            tell(p.chat_id, msg)
            restart(p)
            sleep(0.100) # no more than 10 messages per second
    logging.debug("Succeffully restarted users: " + str(count))
    return count


def init_user(p, name, last_name, username):
    if (p.name.encode('utf-8') != name):
        p.name = name
        p.put()
    if (p.getLastName() != last_name):
        p.last_name = last_name
        p.put()
    if (p.username != username):
        p.username = username
        p.put()
    if not p.enabled:
        p.enabled = True
        p.put()

def get_date_CET(date):
    if date is None: return None
    newdate = date + timedelta(hours=1)
    return newdate

def get_time_string(date):
    newdate = date + timedelta(hours=1)
    return str(newdate).split(" ")[1].split(".")[0]

def broadcast(sender_id, msg, restart_user=False, markdown=False, curs=None, enabledCount = 0):
    #return

    BROADCAST_COUNT_REPORT = utility.unindent(
        """
        Mesage sent to {} people
        Enabled: {}
        Disabled: {}
        """
    )

    users, next_curs, more = Person.query().fetch_page(50, start_cursor=curs)
    try:
        for p in users:
            if p.enabled:
                enabledCount += 1
                if restart_user:
                    restart(p)
                tell(p.chat_id, msg, markdown=markdown, sleepDelay=True)
    except datastore_errors.Timeout:
        sleep(1)
        deferred.defer(broadcast, sender_id, msg, restart_user, markdown, curs, enabledCount)
        return
    if more:
        deferred.defer(broadcast, sender_id, msg, restart_user, markdown, next_curs, enabledCount)
    else:
        total = Person.query().count()
        disabled = total - enabledCount
        msg_debug = BROADCAST_COUNT_REPORT.format(str(total), str(enabledCount), str(disabled))
        tell(sender_id, msg_debug)


def getInfoCount():
    c = Person.query().count()
    msg = "Attualmente siamo in *{0}* persone iscritte a @emojitalianobot! " \
          "Vogliamo crescere insieme, aiutaci a far conoscere questo bot invitando altri amici e " \
          "votandolo su [storebot](telegram.me/storebot?start=emojitalianobot) e su " \
          "[telegramitalia](telegramitalia.it/emojitalianobot)!".format(str(c))
    return msg

def tellmyself(p, msg):
    tell(p.chat_id, "Udiete udite... " + msg)

def tell_masters(msg, markdown=False, one_time_keyboard=False):
    for id in key.MASTER_CHAT_ID:
        tell(id, msg, markdown=markdown, one_time_keyboard = one_time_keyboard, sleepDelay=True)

def tell_fede(msg):
    for i in range(100):
        tell(key.FEDE_CHAT_ID, "prova " + str(i))
        sleep(0.1)

def goToInserisciInGloassario(p, msg=''):
    if msg:
        msg += "\n\n"
    tell(p.chat_id, msg + "INSERISCI una voce nel glossario nel seguente formato: 'emoji|testo' ad esempio:\n" +
          CAPIRE + "|capire" + "\n" + LEGGERE + "|leggere",
          kb=[[BOTTONE_INDIETRO]])
    p.tmpString = None
    person.setState(p, 41)

def goToEliminaFromGloassario(p, msg=''):
    if msg:
        msg += "\n\n"
    tell(p.chat_id, msg + "ELIMINA una voce nel glossario nel seguente formato: 'emoji|testo' ad esempio:\n" +
          CAPIRE + "|capire" + "\n" + LEGGERE + "|leggere",
          kb=[[BOTTONE_INDIETRO]])
    p.tmpString = None
    person.setState(p, 42)

def askToConfirmNormalization(p, emojiNorm, newState):
    txtMsg = CANCEL + "Il testo inserito contiene un emoji non standard." + \
             "\nEmoji normalizzato: " + emojiNorm + \
             "\nConfermi che l'emoji normalizzato è corretto?"
    tell(p.chat_id, txtMsg, kb=[[BOTTONE_SI, BOTTONE_NO]])
    p.tmpString = emojiNorm
    person.setState(p, newState)

def sendGlossarioNotification(p, inserito, emoji_text):
    if WORK_IN_PROGRESS:
        return
    eliminato_inserito = "INSERITO" if inserito else "ELIMINATO"
    msg = BOOK + " " + p.name.encode('utf-8') + " ha " + eliminato_inserito + " la seguente voce nel glossario: " + emoji_text
    for master_chat_id in key.GLOSS_CHANGE_NOTIFICATION:
        if p.chat_id != master_chat_id:
            tell(master_chat_id, msg)


def tell(chat_id, msg, kb=None, markdown=False, inlineKeyboardMarkup=False,
         one_time_keyboard=True, sleepDelay=False):
    replyMarkup = {
        'resize_keyboard': True,
        'one_time_keyboard': one_time_keyboard
    }
    if kb:
        if inlineKeyboardMarkup:
            replyMarkup['inline_keyboard'] = kb
        else:
            replyMarkup['keyboard'] = kb
    try:
        resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
            'chat_id': chat_id,
            'text': msg,
            'disable_web_page_preview': 'true',
            'parse_mode': 'Markdown' if markdown else '',
            # 'reply_to_message_id': str(message_id),
            'reply_markup': json.dumps(replyMarkup),
        })).read()
        logging.info('send response: ')
        logging.info(resp)
        resp_json = json.loads(resp)
        return resp_json['result']['message_id']
    except urllib2.HTTPError, err:
        if err.code == 403:
            p = person.getPersonByChatId(chat_id)
            p.setEnabled(False, put=True)
            # logging.info('Disabled user: ' + p.name.encode('utf-8') + ' ' + str(chat_id))
        else:
            logging.debug('Raising unknown err in tell() with msg = {} and kb={}'.format(msg, kb))
            raise err
    if sleepDelay:
        sleep(0.1)

# ================================
# ================================
# ================================

# ================================
# RESTART
# ================================
def restart(p, msg=None):
    if msg:
        tell(p.chat_id, msg)
    redirectToState(p, 0)

# ================================
# SWITCH TO STATE
# ================================
def redirectToState(p, new_state, **kwargs):
    if p.state != new_state:
        logging.debug("In redirectToState. current_state:{0}, new_state: {1}".format(str(p.state),str(new_state)))
        p.setState(new_state)
    repeatState(p, **kwargs)

# ================================
# REPEAT STATE
# ================================
def repeatState(p, **kwargs):
    methodName = "goToState" + str(p.state)
    method = possibles.get(methodName)
    if not method:
        tell(p.chat_id,
             "Si è verificato un problema. Lo abbiamo comunicato agli amministratori. "
             "Sarai ora reindirizzato alla schermata iniziale.")
        tell(key.FEDE_CHAT_ID,
             "Detected error for user {}: unexisting method {}.".format(p.getUserInfoString(), methodName))
        restart(p)
    else:
        method(p, **kwargs)

# ================================
# ================================
# ================================

# ================================
# GO TO STATE 0: STAT SCREEN
# ================================

def goToState0(p, input=None, **kwargs):
    giveInstruction = input is None
    if giveInstruction:
        keyboard = [[IT_TEXT_TOFROM_EMOJI, EN_TEXT_TOFROM_EMOJI], [BOTTONE_INVITA_AMICO, BOTTONE_INFO]]
        secondLine = [BOTTONE_GIOCA]
        if p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            secondLine.insert(0, BOTTONE_PINOCCHIO)
        keyboard.insert(1, secondLine)
        tell(p.chat_id, "Schermata Iniziale.", kb=keyboard)
        #logging.debug("restart kb: " + str(keyboard))
    else:
        if input in ['/help', BOTTONE_INFO]:
            tell(p.chat_id, ISTRUZIONI)
        elif input == BOTTONE_INVITA_AMICO:
            tell(p.chat_id, INVITE_FRIEND_INSTRUCTION, markdown=True)
            tell(p.chat_id, MESSAGE_FOR_FRIENDS, markdown=True)
        elif input == '/comeInoltrareUnMessaggio':
            tell(p.chat_id, HOW_TO_FORWARD_A_MESSAGE, markdown=True)
        elif input == IT_TEXT_TOFROM_EMOJI:
            randomGlossMultiEmoji = emojiUtil.getRandomGlossMultiEmoji()
            randomGlossMultiEmoji_emoji = randomGlossMultiEmoji.getEmoji()
            randomGlossMultiEmoji_translation = randomGlossMultiEmoji.getFirstTranslation()
            randomSingleEmoji = emojiUtil.getRandomSingleEmoji()
            randomWord = emojiUtil.getRandomUnicodeTag()
            tell(p.chat_id, "Inserisci un emoji, ad esempio {0} o una parola in italiano, ad esempio *{1}*.\n"
                  "Se invece sei interessato in particolare al glossario di Pinocchio puoi inserire anche "
                  "più combinazioni di emoji, ad esempio {2} ({3})".format(
                randomSingleEmoji, randomWord, randomGlossMultiEmoji_emoji, randomGlossMultiEmoji_translation),
                kb=[[BOTTONE_INDIETRO]], markdown=True)
            person.setState(p, 20)
            # state 20
        elif input == EN_TEXT_TOFROM_EMOJI:
            randomEmoji = emojiUtil.getRandomSingleEmoji(italian=False)
            randomWord = emojiUtil.getRandomUnicodeTag(italian=False)
            tell(p.chat_id, "Please entere a single emoji, for instance " + randomEmoji +
                  ", or one or more English words, for instance '" + randomWord + "'", kb=[[BOTTONE_INDIETRO]])
            person.setState(p, 21)
            # state 21
        elif input == BOTTONE_PINOCCHIO and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            redirectToState(p, 30)
        elif input == BOTTONE_GIOCA:
            goToGamePanel(p)
            # state 50
        elif input.lower().strip() == FUTURO_REMOTO_COMMAND:
            if p.chat_id!=key.FEDE_CHAT_ID:
                redirectToState(p, 80)
            else:
                redirectToState(p, 81)
        elif p.chat_id in key.MASTER_CHAT_ID:
            if input == '/test':
                emoji = u'\U0001F1EE\U0001F1F2'
                tell(p.chat_id, emoji.encode('utf-8'))
            elif input == '/testUnicode':
                txt = "Questa è una frase con unicode"
                tell(p.chat_id, txt + " " + str(type(txt)))
            elif input.startswith("/getPinocchioEmojiChapterSentence"):
                input_split = input.split(' ')
                ch = int(input_split[1].strip())
                line = int(input_split[1].strip())
                sentence = pinocchio.getPinocchioEmojiChapterSentence(ch, line)
                tell(p.chat_id, sentence)
            elif input.startswith("/normalizePinocchioChapter"):
                input_split = input.split(' ')
                ch = int(input_split[1].strip())
                result = pinocchio.normalizePinocchioChapter(ch)
                tell(p.chat_id, result)
            elif input.startswith("/getEmojiCodePoint"):
                input_split = input.split(' ')
                e = input_split[1].strip()
                result = emojiUtil.getCodePointWithInitialZeros(e)
                tell(p.chat_id, result)
            elif input.startswith('/testEmoji'):
                if ' ' in input:
                    test = input[input.index(' ') + 1:].replace(' ', '')
                    # test_without_emoji = emojiUtil.getStringWithoutStandardEmojis(test)
                    # msgTxt = "Testo senza emojis: '" + test_without_emoji + "'\n"
                    msgTxt = "Testo inserito: '" + test + "'\n"
                    normalized = emojiUtil.getNormalizedEmojiUtf(test)
                    if emojiUtil.stringHasOnlyStandardEmojis(test):
                        msgTxt += "Il testo contiene solo emoji standard"
                    # elif emojiUtil.stringContainsAnyStandardEmoji(test):
                    #    msgTxt += "Il testo contiene emoji standard e emoji non-standard."
                    #    msgTxt += "\nVersione normalizzata: " + normalized.encode('utf-8')
                    else:
                        msgTxt += "Il testo non contiene emoji standard"
                        msgTxt += "\nVersione normalizzata: " + normalized
                    tell(p.chat_id, msgTxt)
                else:
                    tell(p.chat_id, "Manca uno spazio dopo /testEmoji")
            elif input.startswith('/checkGlossUnicode'):
                glosses = emojiUtil.checkForGlossUniProblems()
                if glosses:
                    tell(p.chat_id, 'Found glosses with potential inconsistencies: ' + str(len(glosses)))
                    glosses_split = utility.makeArray2D(glosses, length=10)
                    # logging.debug(str(glosses))
                    # logging.debug(str(glosses_split))
                    for part in glosses_split:
                        textMsg = ""
                        for g in part:
                            textMsg += gloss.getGlosEmojiAndTargetText(g) + "\n"
                            textMsg += emojiUtil.getStringWithoutStandardEmojis(g.source_emoji.encode('utf-8'))
                            textMsg += "\n\n"
                        tell(p.chat_id, textMsg)
                else:
                    tell(p.chat_id, 'No glosses found with inconsistencies')
            elif input == '/glossStats':
                emojiTranslationsCounts = gloss.getEmojiTranslationsCount()
                textMsg = "Emoji and Translations counts: " + str(emojiTranslationsCounts) + "\n"
                textMsg += "Gaps in numbersing: " + str(gloss.getNumberingGaps())
                tell(p.chat_id, textMsg)
            elif input.startswith('/restartUsers'):
                msgTxt = None
                if ' ' in input:
                    msgTxt = input[input.index(' ') + 1:]
                deferred.defer(restartAllUsers, input)  # 'New interface :)')
            elif input.startswith('/getConfusionWordToEmojis'):
                if ' ' in input:
                    d = confusionTables.getConfusionWordToEmojis(input[input.index(' ') + 1:])
                    textMsg = ""
                    for (k, v) in d.items():
                        textMsg += k.encode('utf-8') + ": " + str(v)
                    tell(p.chat_id, textMsg)
                else:
                    tell(p.chat_id, 'missing text after command')
            elif input.startswith('/getConfusionEmojiToWords'):
                if ' ' in input:
                    tell(p.chat_id, str(confusionTables.getConfusionEmojiToWords(input[input.index(' ') + 1:])))
                else:
                    tell(p.chat_id, 'missing text after command')
            elif input == '/infocount':
                tell(p.chat_id, getInfoCount(), markdown=True)
            elif input.startswith('/broadcast ') and len(input) > 11:
                msg = input[11:]
                deferred.defer(broadcast, p.chat_id, msg, restart_user=False)
            elif input.startswith('/restartBroadcast ') and len(input) > 18:
                msg = input[18:]
                deferred.defer(broadcast, p.chat_id, msg, restart_user=True)
            elif input == '/aggiornaPinocchio':
                pinocchio.buildPinocchioChapters()
                tell(p.chat_id, "Aggiornamento completato!")
            else:
                tell(p.chat_id, 'Scusa, capisco solo /help /start '
                                'e altri comandi segreti...')
        else:
            tell(p.chat_id,
                 "Scusa non capisco quello che hai detto.\n"
                 "Usa i pulsanti sotto o premi /help per avere informazioni.")

# ================================
# GO TO STATE 30: PINOCCHIO
# ================================

def goToState30(p, input=None, **kwargs):
    logging.debug('In state 30')
    giveInstruction = input is None
    kb = [
        [BOTTONE_GLOSSARIO, BOTTONE_GRAMMATICA],
        [BOTTONE_INDIETRO]
    ]
    if giveInstruction:
        msg = "(Area riservata) Premi uno dei pulsanti per entrare nel mondo di PINOCCHIO."
        tell(p.chat_id, msg, kb)
    else:
        if input == BOTTONE_INDIETRO:
            restart(p)
        elif input == BOTTONE_GLOSSARIO and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            tell(p.chat_id, "Vuoi INSERIRE o ELIMINARE una voce nel glossario?",
                 kb=[['INSERIRE', 'ELIMINARE'], [BOTTONE_INDIETRO]])
            person.setState(p, 40)
        elif input == BOTTONE_GRAMMATICA and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            redirectToState(p, 60)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco")

# ================================
# GO TO STATE 60: PINOCCHIO GRAMMATICA
# ================================

def goToState60(p, input=None, **kwargs):
    logging.debug('In state 42')
    giveInstruction = input is None
    kb = [
        [grammar_rules.REGOLE_GENERALI_BUTTON],
        grammar_rules.FUNCTIONAL_EMOJIS,
        [BOTTONE_INDIETRO]
    ]
    if giveInstruction:
        msg = "Premi uno dei pulsanti per avere informazioni sulle corrispondenti regole grammaticali."
        tell(p.chat_id, msg, kb)
    else:
        if input == BOTTONE_INDIETRO:
            restart(p)
        elif input in grammar_rules.GRAMMAR_RULES.keys():
            tell(p.chat_id, grammar_rules.GRAMMAR_RULES[input], kb)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco")

# ================================
# GO TO STATE 80: Futuro Remoto Start Participants
# ================================
ANSWER_BUTTONS = ['A','B','C','D']

def goToState80(p, input=None, **kwargs):
    logging.debug('In state 80: Futuro Remoto')
    giveInstruction = input is None
    if giveInstruction:
        msg = "Benvenuta/o in Futuro Remoto."
        kb = [ANSWER_BUTTONS]
        tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
    else:
        message_timestamp = kwargs['message_timestamp']
        if input in ANSWER_BUTTONS:
            #tell(p.chat_id, "You sent the message at: {}".format(message_timestamp))
            questionNumber, ellapsedSeconds = futuroRemoto.addAnswer(p, input, message_timestamp)
            if ellapsedSeconds == -1:
                # answers are not currently accepted
                msg = 'Mi dispiace, in questo momento le risposte sono bloccate.'
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
            elif ellapsedSeconds == -2:
                # user already answered to the question
                msg = 'Mi dispiace, hai già risposto alla domanda {} del quiz.'.format(questionNumber)
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
            else: # >0
                msg = "Grazie! " \
                      "Hai risposto in {} secondi. " \
                      "La tua risposta ({}) alla domanda {} è stata registrata. ".format(ellapsedSeconds, input, questionNumber)
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco. Rispondi A, B, C o D.")

# ================================
# GO TO STATE 81: Futuro Remoto Start FEDE
# ================================

def goToState81(p, input=None, **kwargs):
    logging.debug('In state 81: Futuro Remoto')
    NEXT_QUESTION_BUTTON = 'NEXT QUESTION'
    STOP_ANSWERS_BUTTON = 'STOP ANSWERS'
    END_QUIZ_BUTTON = 'END QUIZ'
    PEOPLE_IN_QUIZ_BUTTON = 'PEOPLE IN QUIZ'
    GLOBAL_STATS_BUTTON = 'GLOBAL STATS'
    RESET_QUIZ_BUTTON = 'RESET QUIZ'
    WINNING_MSG = [
        "COMPLIMENTI, HAI VINTO IL QUIZ! SALI SUL PALCO A RITIRARE IL PREMIO.",
        "COMPLIMENTI, SEI ARRIVATO/A SECONDO NEL QUIZ! SALI SUL PALCO A RITIRARE IL PREMIO.",
        "COMPLIMENTI, SEI ARRIVATO/A TERZO NEL QUIZ! SALI SUL PALCO A RITIRARE IL PREMIO.",
    ]
    giveInstruction = input is None
    if giveInstruction:
        kb = [
            [NEXT_QUESTION_BUTTON],
            [PEOPLE_IN_QUIZ_BUTTON, GLOBAL_STATS_BUTTON],
            [END_QUIZ_BUTTON, RESET_QUIZ_BUTTON]
        ]
        msg = "Ciao Fede, benvenuto in Futuro Remoto."
        tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
    else:
        if input == END_QUIZ_BUTTON:
            userAnswersTable = futuroRemoto.getUserAnswersTable()
            firstN_chat_id, summary = futuroRemoto.getUserAnswersTableSorted(3)
            tell(p.chat_id, summary, sleepDelay=True, one_time_keyboard=False)
            enuList = list(enumerate(firstN_chat_id))
            deferred.defer(broadcast_quiz_final_msg, p.chat_id, 80, userAnswersTable, restart_user=True)
            sleep(5)
            for i, id in enuList:
                tell(id, WINNING_MSG[i])
            sleep(1)
            restart(p)
        elif input == PEOPLE_IN_QUIZ_BUTTON:
            c = person.getPeopleCountInState(80)
            msg = 'Ci sono {} persone iscritte al quiz.'.format(c)
            tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        elif input == RESET_QUIZ_BUTTON:
            futuroRemoto.resetQuizManager()
            futuroRemoto.deleteAllAnswers()
            msg = 'Quiz risettato con successo'
            tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        elif input == NEXT_QUESTION_BUTTON:
            futuroRemoto.addQuestion()
            kb = [[STOP_ANSWERS_BUTTON]]
            msg = 'Fai la domanda e quando vuoi terminare di accettare risposte premi su {}.'.format(STOP_ANSWERS_BUTTON)
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif input == STOP_ANSWERS_BUTTON:
            futuroRemoto.stopAcceptingAnswers()
            kb = [ANSWER_BUTTONS]
            msg = 'Le risposte sono state bloccate. Inserisci la risposta corretta.'
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif input in ANSWER_BUTTONS:
            resultTable, correctNamesTimeSorted = futuroRemoto.validateAnswers(input)
            correctNamesStr = ', '.join([x.encode('utf-8') for x in correctNamesTimeSorted])
            msg = 'Le risposte sono state validate. \n' \
                  'Le persone che hanno indovinato sono {}: {}'.format(len(correctNamesTimeSorted), str(correctNamesStr))
            kb = [
                [NEXT_QUESTION_BUTTON],
                [PEOPLE_IN_QUIZ_BUTTON, GLOBAL_STATS_BUTTON],
                [END_QUIZ_BUTTON, RESET_QUIZ_BUTTON]
            ]
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif input == GLOBAL_STATS_BUTTON:
            firstN_chat_id, summary = futuroRemoto.getUserAnswersTableSorted()
            tell(p.chat_id, summary, sleepDelay=True, one_time_keyboard=False)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco")

def broadcast_quiz_final_msg(sender_id, state, userAnswersTable, restart_user=False, markdown=False, curs=None):
    users, next_curs, more = Person.query(Person.state == state).fetch_page(50, start_cursor=curs)
    try:
        for p in users:
            if p.enabled:
                if restart_user:
                    restart(p)
                msg = futuroRemoto.getUserSpecificSummary(p, userAnswersTable),
                tell(p.chat_id, msg, sleepDelay=True)
    except datastore_errors.Timeout:
        sleep(1)
        deferred.defer(broadcast_quiz_final_msg, sender_id, state, userAnswersTable, restart_user, markdown, curs)
        return
    if more:
        deferred.defer(broadcast_quiz_final_msg, sender_id, state, userAnswersTable, restart_user, markdown, next_curs)
    else:
        msg_debug = "Messagio finale inviato."
        tell(sender_id, msg_debug)


# ================================
# ================================
# ================================

def goToGamePanel(p):
    tell(p.chat_id, "Per il momento abbiamo due semplici giochi attivi: " +
          "puoi indovinare un emoji a partire da una parola (" + IT_TO_EMOJI + ") " +
          "oppure viceversa  (" + EMOJI_TO_IT + ")",
          kb=[[IT_TO_EMOJI, EMOJI_TO_IT], [BOTTONE_INDIETRO]])
    person.setState(p, 50)

def playWordToEmoji(p):
    g = gloss.getRandomGloss()
    it_words = g.target_text
    index = randint(0, len(it_words)-1)
    selected_it_word = it_words[index].encode('utf-8')
    tell(p.chat_id, "Prova a indovinare l'equivalente in emoji della parola '" +
          selected_it_word + "'", kb=[['UN AIUTO?'],[BOTTONE_INDIETRO]])
    p.tmpInt = index
    p.glossGame = g
    person.setState(p, 51)

def aiutinoWordToEmoji(p):
    g = p.glossGame
    options = gloss.getConfusionEmoji(g,4)
    kb = utility.makeArray2D(options, 2)
    kb.append([BOTTONE_INDIETRO])
    tell(p.chat_id, "Ecco alcune possibilità: ", kb)

def playEmojiToWord(p):
    g = gloss.getRandomGloss()
    emoji = g.source_emoji.encode('utf-8')
    tell(p.chat_id, "Prova a indovinare una possibile traduzione in italiano di " +
          emoji, kb=[['UN AIUTO?'],[BOTTONE_INDIETRO]])
    p.glossGame = g
    person.setState(p, 52)

def aiutinoEmojiToWord(p):
    g = p.glossGame
    if not g:
        tell(p.chat_id, "Si è verificato un problema, ti prego di contattare @kercos per segnalarlo, grazie!")
        logging.warning("Probelm in aiutinoEmojiToWord: p.glossGame==None")
    else:
        options = gloss.getConfusionTranslations(g,4)
        kb = utility.makeArray2D(options, 2)
        kb.append([BOTTONE_INDIETRO])
        tell(p.chat_id, "Ecco alcune possibilità: ", kb)




# ================================
# ================================
# ================================

def getEmojiListFromTagInDictAndGloss(string):
    result = set()
    emojiList = emojiUtil.getEmojisForTag(string)
    if emojiList:
        result.update([tag_emoji for tag_emoji in emojiList])
    gloss_emoji_list = gloss.getEmojiListFromText(string)
    if gloss_emoji_list:
        result.update([gloss_emoji for gloss_emoji in gloss_emoji_list])
    return list(result)

def getEmojiFromString(string, italian=True):

    if emojiUtil.stringContainsAnyStandardEmoji(string):
        return "Il testo inserito non deve contenere emoji"

    gloss_emoji_list = gloss.getEmojiListFromText(string)

    msg = []
    emojiList = emojiUtil.getEmojisForTag(string, italian)

    if italian:
        found = False
        if gloss_emoji_list:
            found = True
            gloss_emoji_list_str = ', '.join(gloss_emoji_list)
            msg.append('Trovata voce nel glossario: ' + string + " = " + gloss_emoji_list_str)
        if emojiList:
            found = True
            emojisListStr = ', '.join(set(emojiList))
            msg.append('Trovati emoji in tabella unicode con questo tag: ' + emojisListStr)
        if not found:
            msg.append("Nessun emoji trovato per la stringa inserita")
    else:
        if emojiList:
            emojisListStr = ', '.join(set(emojiList))
            msg.append('Found the following emojis in the unicode table with the given tag: ' + emojisListStr)
        else:
            msg.append("Nessun emoji trovato per la stringa inserita")

    return '\n'.join(msg)



def getStringFromEmoji(input_emoji, italian=True, pinocchioSearch=False):

    msg = ''

    if not emojiUtil.stringHasOnlyStandardEmojis(input_emoji):
        input_emoji = emojiUtil.getNormalizedEmojiUtf(input_emoji)
        if italian:
            msg += EXCLAMATION + " Il testo inserito contiene emoji non standard.\n" + \
                   "Provo a normalizzarlo: " + input_emoji + '\n\n'
        else:
            msg += EXCLAMATION + " The inserted text contains non-standard emojis.\n" + \
                   "I'm trying to normalize it: " + input_emoji + '\n\n'

    tags = emojiUtil.getTagsForEmoji(input_emoji, italian)
    found = False

    if italian:
        gloss_text = gloss.getTextFromEmoji(input_emoji)
        if gloss_text:
            found = True
            words = ', '.join([x.encode('utf-8') for x in gloss_text])
            msg += 'Trovata voce nel glossario: ' + input_emoji + " = " + words + '\n'
        if pinocchioSearch:
            msg += 'Occorrenze in Pinochio (ricerca parole): ' + ' '.join(
                pinocchio.findEmojiInPinocchio(input_emoji)) + '\n'
            msg += 'Occorrenze in Pinochio (ricerca completa): ' + ' '.join(
                pinocchio.findEmojiInPinocchio(input_emoji,deepSearch=True)) + '\n'
        if tags:
            found = True
            annotations = ', '.join(tags)
            msg += "Trovato emoji in tabella unicode con questi tags: " + annotations + '\n'
        if not found:
            msg += "L'emoji inserito non è presente nel glossario o nella tabella unicode." + '\n'
    else:
        if tags:
            found = True
            annotations = ', '.join(tags)
            msg += "Found emoji in unicode table with the following tags: " + annotations + '\n'
        description = emojiUtil.getDescriptionForEmoji(input_emoji)
        if description:
            msg += "and the following description (identification string): " + description + '\n'
        if not found:
            msg += "The emoji you have inserted is not present in the unicode table." + '\n'

    return msg

# ================================
# INLINE QUERY
# ================================

EMOJI_PNG_URL = 'https://dl.dropboxusercontent.com/u/12016006/Emoji/png_one/'
EMOJI_IN_GLOSS_PNG_URL = 'https://dl.dropboxusercontent.com/u/12016006/Emoji/glossary.png'

def getEmojiThumbnailUrl(e):
    if e in emojiUtil.ALL_EMOJIS:
        codePoints = emojiUtil.getCodePointWithInitialZeros(e)
        return EMOJI_PNG_URL + codePoints + ".png"
    else:
        e = "🏃"
        codePoints = emojiUtil.getCodePointWithInitialZeros(e)
        return EMOJI_PNG_URL + codePoints + ".png"
        #return EMOJI_IN_GLOSS_PNG_URL


ADD_TEXT_TO_EMOJI_IN_INLINE_QUERY = True

def createInlineQueryResultArticle(id, tag, query_offset):
    emojiList = getEmojiListFromTagInDictAndGloss(tag)
    query_offset_int = int(query_offset) if query_offset else 0
    start_index = 50*query_offset_int
    end_index = start_index + 50
    hasMore = len(emojiList)>end_index
    emojiList = emojiList[start_index:end_index]
    #logging.debug("Replying to inline query for tag '" + tag + "'")
    if emojiList:
        result = []
        i = 0
        for e in emojiList:
            msg = e
            if ADD_TEXT_TO_EMOJI_IN_INLINE_QUERY:
                msg += ' (' + tag + ')'
            result.append(
                {
                    'type': "article",
                    'id': str(id) + '/' + str(i),
                    'title': e,
                    'message_text': msg,
                    'hide_url': True,
                    'thumb_url': getEmojiThumbnailUrl(e),
                }
            )
            i += 1
    else:
        msg = 'Nessun emoji trovato per questa parola'
        if ADD_TEXT_TO_EMOJI_IN_INLINE_QUERY:
            msg += ' (' + tag + ')'
        result = [{
            'type': "article",
            'id': str(id) + '/0',
            'title': msg,
            'message_text': msg,
            'hide_url': True,
        }]
    next_offset = str(query_offset_int+1) if hasMore else ''
    return next_offset, result

def answerInlineQuery(query_id, inlineQueryResults, next_offset):
    my_data = {
        'inline_query_id': query_id,
        'results': json.dumps(inlineQueryResults),
        'is_personal': False,
        'cache_time': 0, #default 300
        'next_offset': next_offset
    }
    try:
        resp = urllib2.urlopen(BASE_URL + 'answerInlineQuery',
                               urllib.urlencode(my_data)).read()
        logging.info('send response: ')
        logging.info(resp)
    except urllib2.HTTPError, err:
        if err.code == 400:
            logging.error('HTTPError 400 in answerInlineQuery. MyData:' + str(my_data))
            tell(key.FEDE_CHAT_ID, 'HTTPError 400 in answerInlineQuery. MyData:' + str(my_data))

def dealWithInlineQuery(body):
    inline_query = body['inline_query']
    query_text = inline_query['query'].encode('utf-8').strip()
    if len(query_text)>0:
        #logging.debug('inline query text: ' + query_text)
        query_id = inline_query['id']
        query_offset = inline_query['offset']
        #chat_id = inline_query['from']['id']
        next_offset, query_results = createInlineQueryResultArticle(query_id, query_text, query_offset)
        answerInlineQuery(query_id, query_results, next_offset)




# ================================
# ================================
# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class InfouserAllHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        msg = getInfoCount()
        broadcast(key.FEDE_CHAT_ID, msg, markdown=True)

# ================================
# ================================
# ================================


class WebhookHandler(webapp2.RequestHandler):

    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        # update_id = body['update_id']
        if 'inline_query' in body:
            dealWithInlineQuery(body)
        if 'message' not in body:
            return
        message = body['message']
        #message_id = message.get('message_id')
        # date = message.get('date')
        if "chat" not in message:
            return
        # fr = message.get('from')
        message_timestamp = int(message['date'])
        chat = message['chat']
        chat_id = chat['id']
        if "first_name" not in chat:
            return
        text = message.get('text').encode('utf-8') if "text" in message else ''
        name = chat["first_name"].encode('utf-8')
        last_name = chat["last_name"].encode('utf-8') if "last_name" in chat else None
        username = chat["username"] if "username" in chat else None

        def reply(msg=None, kb=None, markdown=True, inlineKeyboardMarkup=False):
            tell(chat_id, msg, kb=kb, markdown=markdown, inlineKeyboardMarkup=inlineKeyboardMarkup)

        p = ndb.Key(Person, str(chat_id)).get()

        if p is None:
            # new user
            logging.info("Text: " + text)
            if text == '/help':
                reply(ISTRUZIONI)
            elif text.startswith("/start"):
                p = person.addPerson(chat_id, name)
                reply("Ciao " + name + ", " + "benvenuta/o!")
                init_user(p, name, last_name, username)
                restart(p)
                # state = -1 or -2
                tell_masters("New user: " + name)
            else:
                reply("Premi su /start se vuoi iniziare. "
                      "Se hai qualche domanda o suggerimento non esitare di contattarmi cliccando su @kercos")
        else:
            # known user
            if text=='':
                reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
            elif text.startswith("/start"):
                reply("Ciao " + name + ", " + "ben ritrovata/o!")
                init_user(p, name, last_name, username)
                restart(p)
                # state = 0
            elif text=='/state':
              if p.state in STATES:
                  reply("You are in state " + str(p.state) + ": " + STATES[p.state])
              else:
                  reply("You are in state " + str(p.state))
            elif WORK_IN_PROGRESS and p.chat_id!=key.FEDE_CHAT_ID:
                reply(UNDER_CONSTRUCTION + " Il sistema è in aggiornamento, riprova più tardi.")
            elif p.state == 20:
                # IT <-> EMOJI
                if text == BOTTONE_INDIETRO:
                    restart(p)
                else:
                    if has_roman_chars(text):
                        emoji = getEmojiFromString(text)
                        reply(emoji, kb=[[BOTTONE_INDIETRO]])
                    else:
                        string = getStringFromEmoji(text, italian=True, pinocchioSearch=p.isAdmin())
                        reply(string, kb = [[BOTTONE_INDIETRO]])
            elif p.state == 21:
                # EN <-> EMOJI
                if text == BOTTONE_INDIETRO:
                    restart(p)
                else:
                    if has_roman_chars(text):
                        emoji = getEmojiFromString(text, italian=False)
                        reply(emoji, kb=[[BOTTONE_INDIETRO]])
                    else:
                        string = getStringFromEmoji(text, italian=False)
                        reply(string, kb=[[BOTTONE_INDIETRO]])
            elif p.state == 40:
                if text == BOTTONE_INDIETRO:
                    restart(p)
                    # state = 0
                elif text == 'INSERIRE':
                    goToInserisciInGloassario(p)
                    # state 41
                elif text == 'ELIMINARE':
                    goToEliminaFromGloassario(p)
                    # state 42
                else:
                    reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
            elif p.state == 41:
                # GLOASSARIO INSERISCI VOCE
                if text == BOTTONE_INDIETRO:
                    restart(p)
                    # state = -1
                else:
                    if p.tmpString:
                        if text == BOTTONE_SI:
                            text_strip = p.tmpString.encode('utf-8')
                        elif text == BOTTONE_NO:
                            goToInserisciInGloassario(p, "Inserimento Annullato.")
                            return
                        else:
                            reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
                            return
                    else:
                        text_strip = text.strip()
                    split = text_strip.split('|')
                    if len(split)==2 and len(split[0])>0 and len(split[1])>0:
                        word = split[1].strip()
                        emoji = split[0].replace(' ','')
                        if emojiUtil.stringHasOnlyStandardEmojis(emoji):
                            present_emojis = gloss.getEmojiListFromText(word)
                            txtMsg = ''
                            if present_emojis:
                                if emoji in present_emojis:
                                    txtMsg = CANCEL + " L'emoji " + emoji + " è già associato al testo '" + word + "'"
                                    goToInserisciInGloassario(p, txtMsg)
                                    return
                                present_emoji_str = ', '.join(present_emojis)
                                txtMsg += EXCLAMATION + " Omonimia! " \
                                          "Parola già presente nel glossario associata a questo/i emoji: " + \
                                          present_emoji_str + "\n\n"
                            sendGlossarioNotification(p, True, text_strip)
                            present_gloss = gloss.getGlossFromEmoji(emoji)
                            if present_gloss:
                                gloss.appendTargetText(p, present_gloss, word)
                                present_words = present_gloss.target_text
                                words = [x.encode('utf-8') for x in present_words]
                                txtMsg += CHECK + "Voce aggiornata nel glossario: " + emoji + \
                                          "|" + ', '.join(words) + \
                                          "\nGrazie! " + CLAPPING_HANDS
                                goToInserisciInGloassario(p, txtMsg)
                            else:
                                gloss.addGloss(p, emoji, word)
                                txtMsg += CHECK + " Voce inserita nel glossario, grazie! " + CLAPPING_HANDS
                                goToInserisciInGloassario(p, txtMsg)
                        else:
                            emojiNorm = emojiUtil.getNormalizedEmojiUtf(emoji)
                            emojiNorm_word = emojiNorm + "|" + word
                            askToConfirmNormalization(p, emojiNorm_word, 41)
                    else:
                        txtMsg = CANCEL + " Input non valido."
                        goToInserisciInGloassario(p, txtMsg)
            elif p.state == 42:
                # GLOASSARIO ELIMINA VOCE
                if text == BOTTONE_INDIETRO:
                    restart(p)
                    # state = -1
                else:
                    if p.tmpString:
                        if text == BOTTONE_SI:
                            text_strip = p.tmpString.encode('utf-8')
                        elif text == BOTTONE_NO:
                            goToEliminaFromGloassario(p, "Eliminazione Annullata.")
                            return
                        else:
                            reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
                            return
                    else:
                        text_strip = text.strip()
                    split = text_strip.split('|')
                    if len(split)==2 and len(split[0])>0 and len(split[1])>0:
                        word = split[1].strip()
                        emoji = split[0].replace(' ','')
                        if emojiUtil.stringHasOnlyStandardEmojis(emoji):
                            present_gloss = gloss.getGloss(emoji, word)
                            if present_gloss:
                                # sendGlossarioNotification(p, False, emoji + '|' + word)
                                sendGlossarioNotification(p, False, text_strip)
                                if len(present_gloss.target_text) == 1:
                                    gloss.deleteGloss(present_gloss)
                                    txtMsg = CHECK + " Voce eliminata dal glossario, grazie! " + CLAPPING_HANDS
                                    goToEliminaFromGloassario(p, txtMsg)
                                else:
                                    if gloss.deleteEntry(p, present_gloss, word):
                                        present_words = present_gloss.target_text
                                        words = [x.encode('utf-8') for x in present_words]
                                        txtMsg = CHECK + " Voce eliminata dal glossario! " +\
                                                 "L'emoji rimane associato alle seguenti parole:\n" + \
                                                 emoji + "|" + ', '.join(words)
                                        goToEliminaFromGloassario(p, txtMsg)
                                    else:
                                        txtMsg = CANCEL + ' Non riesco ad eliminare questa voce.'
                                        goToEliminaFromGloassario(p, txtMsg)
                            else:
                                txtMsg = CANCEL + " Voce non presente nel glossario."
                                goToEliminaFromGloassario(p, txtMsg)
                        else:
                            emojiNorm = emojiUtil.getNormalizedEmojiUtf(emoji)
                            emojiNorm_word = emojiNorm + "|" + word
                            askToConfirmNormalization(p, emojiNorm_word, 42)
                    else:
                        txtMsg = CANCEL + " Input non valido."
                        goToEliminaFromGloassario(p, txtMsg)
            elif p.state == 50:
                #GAME PANEL
                if text == BOTTONE_INDIETRO:
                    restart(p)
                    #state 0
                elif text==IT_TO_EMOJI:
                    playWordToEmoji(p)
                    # state 51
                elif text==EMOJI_TO_IT:
                    playEmojiToWord(p)
                    # state 52
                else:
                    reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
            elif p.state == 51:
                # WORD TO EMOJI GAME
                if text == 'GIOCA DI NUOVO':
                    playWordToEmoji(p)
                    # state 51
                elif text == BOTTONE_INDIETRO:
                    goToGamePanel(p)
                    # state 50
                elif text == 'UN AIUTO?':
                    aiutinoWordToEmoji(p)
                elif p.glossGame:
                    text = text.strip() #.replace(' ','')
                    warning = ''
                    if not emojiUtil.stringHasOnlyStandardEmojis(text):
                        text = emojiUtil.getNormalizedEmojiUtf(text)
                        reply(CANCEL + "La stringa inserita contiene emoji non standard. " +
                              "Emoji normalizzato: " + text)
                        return
                    answer = p.glossGame.source_emoji.encode('utf-8')
                    word = p.glossGame.target_text[p.tmpInt]
                    confusionTables.addConfusionWordToEmojis(word, text.decode('utf-8'))
                    p.glossGame = None
                    p.put()
                    if text == answer:
                        reply("Hai indovinato!", kb=[['GIOCA DI NUOVO'],[BOTTONE_INDIETRO]])
                    else:
                        intersection = set(text.decode('utf-8')).intersection(answer.decode('utf-8'))
                        if intersection:
                            reply("Quasi giusto! La risposta corretta è " + answer,
                                  kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                        else:
                            reply("Mi dispiace. La risposta corretta è " + answer,
                                  kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                else:
                    reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
            elif p.state == 52:
                # EMOJI TO WORD GAME
                if text == BOTTONE_INDIETRO:
                    goToGamePanel(p)
                    # state 50
                elif text == 'UN AIUTO?':
                    aiutinoEmojiToWord(p)
                elif text == 'GIOCA DI NUOVO':
                    playEmojiToWord(p)
                    # state 52
                elif p.glossGame:
                    text = text.strip().lower()
                    if emojiUtil.stringContainsAnyStandardEmoji(text):
                        reply("Il testo inserito non può contenere emojis.")
                        return
                        #stai in the same state
                    possible_answers = [x.encode('utf-8').lower() for x in p.glossGame.target_text]
                    confusionTables.addConfusionEmojiToWords(p.glossGame.source_emoji, text)
                    p.glossGame = None
                    p.put()
                    if text in possible_answers:
                        other_solutions = list(possible_answers)
                        other_solutions.remove(text)
                        #other_solutions = [x.encode('utf-8') for x in other_solutions]
                        if other_solutions:
                            reply("Hai indovinato! Le altre possibili traduzioni sono: " + ', '.join(other_solutions),
                                  kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                        else:
                            reply("Hai indovinato!", kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                    else:
                        if len(possible_answers)==1:
                            answer = possible_answers[0]
                            reply("Mi dispiace. La risposta corretta è: " + answer,
                                  kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                        else:
                            answers = ', '.join(possible_answers)
                            reply("Mi dispiace. Le possibili traduzioni sono: " + answers,
                                  kb=[['GIOCA DI NUOVO'], [BOTTONE_INDIETRO]])
                else:
                    reply(FROWNING_FACE + " Scusa non capisco quello che hai detto.")
            else:
                logging.debug("Sending {} to state {}. Input: '{}'".format(p.getUserInfoString(), p.state, text))
                repeatState(p, input=text, message_timestamp=message_timestamp)

    def handle_exception(self, exception, debug_mode):
        logging.exception(exception)
        tell(key.FEDE_CHAT_ID, "❗ Detected Exception: " + str(exception))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
#    ('/_ah/channel/connected/', DashboardConnectedHandler),
#    ('/_ah/channel/disconnected/', DashboardDisconnectedHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/infouser_weekly_all', InfouserAllHandler),
    ('/glossario', gloss.GlossarioTableHtml),
], debug=True)

possibles = globals().copy()
possibles.update(locals())
