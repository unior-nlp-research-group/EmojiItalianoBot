# -*- coding: utf-8 -*-

# Set up requests
# see https://cloud.google.com/appengine/docs/standard/python/issue-requests#issuing_an_http_request
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()
#disable warnings
import requests
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.contrib.appengine.AppEnginePlatformWarning
)

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
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.ext.db import datastore_errors

import webapp2
from random import randint
import confusionTables
import emojiUtil
import emojiTags
import utility
import pinocchio
import costituzione
import grammar_rules
import quizGame
import date_util
import re

# ================================
# ================================
# ================================

WORK_IN_PROGRESS = False
FUTURO_REMOTO_ON = False
PINOCHHIO_PUBLIC_ACCESS = False

# ================================
# ================================
# ================================


TELEGRAM_API_BASE_URL = 'https://api.telegram.org/bot' + key.TOKEN + '/'
BASE_URL_FILE = 'https://api.telegram.org/bot/file/bot' + key.TOKEN + '/'

ISTRUZIONI =  \
"""
@emojitalianobot è un tool gratuito e aperto alla comunità per costruire un dizionario italiano degli emoji.

Hai la possibilità di cercare parole o emoji inserite nel glossario di Emojitaliano usato per tradurre \
[Pinocchio](scritturebrevi.it/2016/02/05/pinocchio-in-emojitaliano-the-emoji-column) \
e la [Costituzione](https://www.scritturebrevi.it/2016/10/18/la-costituzione-in-emojitaliano-marina-pierani-libro-delle-firme/):

Se hai bisogno di aiuto o vuoi aiutarci a migliorare il bot vieni nel gruppo di discussione cliccando \
[--> QUI <--](telegram.me/joinchat/B8zsMQg_NUYAROsKeUe8Xw)

Aiutaci a far conoscere questo bot invitando altri amici e votandolo su \
[telegramitalia](telegramitalia.it/emojitalianobot) \
e su [storebot](telegram.me/storebot?start=emojitalianobot).

Per maggiori informazioni visita scritturebrevi.it/emojitalianobot

@emojitalianobot v.7 (ultima modifica 19 Apr 2018)
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

INSERISCI_ELIMINA_VOCE_TEXT = lambda ins_eli: utility.unindent(
    """
    {} una voce nel glossario nel seguente formato: 'emoji|testo' ad esempio:
    {}|capire
    {}|leggere
    """.format(ins_eli, CAPIRE, LEGGERE)
)

CONFIRM_NORM_TEXT = lambda emojiNorm: utility.unindent(
    """
    {} Il testo inserito contiene un emoji non standard.
    Emoji normalizzato: {}
    Confermi che l'emoji normalizzato è corretto?
    """.format(CANCEL, emojiNorm)
)

# ================================
# STATES
# ================================


STATES = {
    0:  'Initial Screen',
    10: 'GRAMMATICA EMOJITALIANO',
    20: 'IT <-> EMOJI',
    21: 'EN <-> EMOJI',
    30: 'PINOCCHIO',
    310:  'GLOSSARIO PINOCCHIO',
    311:    'GLOSSARIO: INSERISCI VOCE',
    312:    'GLOSSARIO: ELIMINA VOCE',
    330:  'LEGGI PINOCCHIO - scegli capitolo',
    331:    'LEGGI PINOCCHIO - frasi capitolo',
    40: 'COSTITUZIONE',
    50: 'GAME PANEL',
    51: 'GAME PANEL -> word to emoji',
    52: 'GAME PANEL -> emoji to word',
    80: 'Quiz',
    81:   'Quiz Participants',
    82:   'Quiz Admin'
}

CANCEL = '❌'
CHECK = '✅'

THUMB = '👍'
FOOTPRINTS = '👣'
NOENTRY = '🚫'
CLAPPING_HANDS = '👏'
SMILING_FACE = '😊'
GEAR = '⚙️'
LEFTWARDS_BLACK_ARROW = '⬅'
BLACK_RIGHTWARDS_ARROW = '➡'
LETTERS = '🔠'
SMILY = '😊'
RIGHT_ARROW = '➡'

IT_FLAG = '🇮🇹'
EN_FLAG = '🇬🇧'


IT_TO_EMOJI = IT_FLAG + ' ' + RIGHT_ARROW + ' ' + SMILY
EMOJI_TO_IT = SMILY + ' ' + RIGHT_ARROW + ' ' + IT_FLAG
EN_TO_EMOJI = EN_FLAG + ' ' + RIGHT_ARROW + ' ' + SMILY
EMOJI_TO_EN = SMILY + ' ' + RIGHT_ARROW + ' ' + EN_FLAG

IT_TEXT_TOFROM_EMOJI = '🇮🇹🔠 ↔ 😊'
EN_TEXT_TOFROM_EMOJI = '🇬🇧🔠 ↔ 😊'

CAPIRE = '💡'
LEGGERE = '👀📖'
BOOK = '📖'
PINOCCHIO = '🏃'
SOS = '🆘'
INFO = 'ℹ'
JOKER = '🃏'
MASCHERE = '🎭'
WARNING_SIGN = '⚠️'
EXCLAMATION = '❗'
UNDER_CONSTRUCTION = '🚧'
FROWNING_FACE = '🙁'


BOTTONE_ANNULLA = CANCEL + " Annulla"
BOTTONE_INDIETRO = LEFTWARDS_BLACK_ARROW + ' ' + "Indietro"
BOTTONE_PINOCCHIO = PINOCCHIO + ' PINOCCHIO'
BOTTONE_COSTITUZIONE = '📜 COSTITUZIONE'
BOTTONE_GLOSSARIO = PINOCCHIO + '📖 GLOSSARIO'
BOTTONE_GRAMMATICA = '🔤📐 GRAMMATICA'
BOTTONE_INFO = INFO + ' INFO'
BOTTONE_GIOCA = JOKER + ' GIOCA!'
BOTTONE_INVITA_AMICO = MASCHERE + ' INVITA UN AMICO'
BOTTONE_SI = CHECK + ' SI'
BOTTONE_NO = CANCEL + ' NO'

INSERIRE_GLOSSARIO_BUTTON = '⤵ INSERIRE'
ELIMINARE_GLOSSARIO_BUTTON = '❌ ELIMINARE'
LISTA_REGOLE_BUTTON = '📐 LISTA REGOLE'
LEGGGI_PINOCCHIO_BUTTON = PINOCCHIO + '📗 LEGGI PINOCCHIO'
NEXT_BUTTON = '⏭ succ.'
PREV_BUTTON = '⏮ prec.'
BOTTONE_INDICE = '👆 indice'

BUTTON_FUTURO_REMOTO = "FUTURO REMOTO"
BUTTON_QUIZ = "QUIZ"
BUTTON_START_QUIZ = "INIZIA QUIZ"
BUTTON_REFRESH = "AGGIORNA"



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
    msg = "Siamo in *{0}* persone iscritte a @emojitalianobot! " \
          "Vogliamo crescere insieme, aiutaci a far conoscere questo bot invitando altri amici e " \
          "votandolo su [storebot](telegram.me/storebot?start=emojitalianobot) e su " \
          "[telegramitalia](telegramitalia.it/emojitalianobot)!".format(str(c))
    return msg

def tellmyself(p, msg):
    tell(p.chat_id, "Udiete udite... " + msg)

def tell_masters(msg, markdown=False, one_time_keyboard=False):
    for chat_id in key.MASTER_CHAT_ID:
        tell(chat_id, msg, markdown=markdown, one_time_keyboard = one_time_keyboard, sleepDelay=True)

def tell_emojitalia_group(msg, markdown=False):
    tell(key.EMOJITALIA_GROUP_ID, msg, markdown=markdown)

def tell_fede(msg):
    for i in range(100):
        tell(key.FEDE_CHAT_ID, "prova " + str(i))
        sleep(0.1)

def sendGlossarioNotification(p, inserito, emoji_text):
    if WORK_IN_PROGRESS:
        return
    eliminato_inserito = "INSERITO" if inserito else "ELIMINATO"
    msg = BOOK + " " + p.name.encode('utf-8') + " ha " + eliminato_inserito + " la seguente voce nel glossario: " + emoji_text
    for master_chat_id in key.GLOSS_CHANGE_NOTIFICATION:
        if p.chat_id != master_chat_id:
            tell(master_chat_id, msg)

def tell(chat_id, msg, kb=None, markdown=False, inlineKeyboardMarkup=False,
         one_time_keyboard=False, sleepDelay=False):
    from google.appengine.api import urlfetch
    urlfetch.set_default_fetch_deadline(60)
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
        data = {
            'chat_id': chat_id,
            'text': msg,
            'disable_web_page_preview': 'true',
            'parse_mode': 'Markdown' if markdown else '',
            'reply_markup': json.dumps(replyMarkup),
        }
        resp = requests.post(TELEGRAM_API_BASE_URL + 'sendMessage', data)
        logging.info('Response: {}'.format(resp.text))
        #logging.info('Json: {}'.format(resp.json()))
        respJson = json.loads(resp.text)
        success = respJson['ok']
        if success:
            if sleepDelay:
                sleep(0.1)
            return True
        else:
            status_code = resp.status_code
            error_code = respJson['error_code']
            description = respJson['description']
            if error_code == 403:
                # Disabled user
                p = person.getPersonByChatId(chat_id)
                p.setEnabled(False, put=True)
                logging.info('Disabled user: ' + p.getUserInfoString())
            elif error_code == 400 and description == "INPUT_USER_DEACTIVATED":
                p = person.getPersonByChatId(chat_id)
                p.setEnabled(False, put=True)
                debugMessage = '❗ Input user disactivated: ' + p.getUserInfoString()
                logging.debug(debugMessage)
                tell(key.FEDE_CHAT_ID, debugMessage, markdown=False)
            else:
                debugMessage = '❗ Raising unknown err in tell() when sending msg={} kb={}.' \
                          '\nStatus code: {}\nerror code: {}\ndescription: {}.'.format(
                    msg, kb, status_code, error_code, description)
                logging.error(debugMessage)
                tell(key.FEDE_CHAT_ID, debugMessage, markdown=False)
    except:
        report_exception()

def tell_person(chat_id, msg, markdown=False):
    tell(chat_id, msg, markdown=markdown)
    p = person.getPersonByChatId(chat_id)
    if p and p.enabled:
        return True
    return False


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
def redirectToState(p, new_state, *args, **kwargs):
    if p.state != new_state:
        logging.debug("In redirectToState. current_state:{0}, new_state: {1}".format(str(p.state),str(new_state)))
        p.setState(new_state)
    repeatState(p, *args, **kwargs)

# ================================
# REPEAT STATE
# ================================
def repeatState(p, *args, **kwargs):
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
        method(p, *args, **kwargs)

# ================================
# ================================
# ================================

# ================================
# UNIVERSAL COMMANDS
# ================================

def dealWithUniversalCommands(p, text_input):
    if p.chat_id in key.MASTER_CHAT_ID:
        if text_input == '/aggiorna':
            pinocchio.buildPinocchioChapters()
            grammar_rules.buildGrammarRules()
            tell(p.chat_id, "Aggiornamento completato!")
    return False


# ================================
# GO TO STATE 0: STAT SCREEN
# ================================

def goToState0(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        keyboard = [[IT_TEXT_TOFROM_EMOJI, EN_TEXT_TOFROM_EMOJI], [BOTTONE_INVITA_AMICO, BOTTONE_GIOCA, BOTTONE_INFO]]
        secondLine = [BOTTONE_GRAMMATICA, BOTTONE_COSTITUZIONE]
        if p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            secondLine.insert(1, BOTTONE_PINOCCHIO)
        keyboard.insert(1, secondLine)
        tell(p.chat_id, "Schermata Iniziale.", kb=keyboard)
        #logging.debug("restart kb: " + str(keyboard))
    else:
        if text_input in ['/help', BOTTONE_INFO]:
            tell(p.chat_id, ISTRUZIONI, markdown=True)
        elif text_input == BOTTONE_INVITA_AMICO:
            tell(p.chat_id, INVITE_FRIEND_INSTRUCTION, markdown=True)
            tell(p.chat_id, MESSAGE_FOR_FRIENDS, markdown=True)
        elif text_input == '/comeInoltrareUnMessaggio':
            tell(p.chat_id, HOW_TO_FORWARD_A_MESSAGE, markdown=True)
        elif text_input == IT_TEXT_TOFROM_EMOJI:
            randomGlossMultiEmoji = gloss.getRandomGlossMultiEmoji()
            randomGlossMultiEmoji_emoji = randomGlossMultiEmoji.getEmoji()
            randomGlossMultiEmoji_translation = randomGlossMultiEmoji.getFirstTranslation()
            randomSingleEmoji = emojiTags.getRandomSingleEmoji()
            randomWord = emojiTags.getRandomTag()
            tell(p.chat_id, "Inserisci un emoji, ad esempio {0} o una parola in italiano, ad esempio *{1}*.\n"
                  "Se invece sei interessato in particolare al glossario di Emojitaliano puoi inserire anche "
                  "più combinazioni di emoji, ad esempio {2} ({3})".format(
                randomSingleEmoji, randomWord, randomGlossMultiEmoji_emoji, randomGlossMultiEmoji_translation),
                kb=[[BOTTONE_INDIETRO]], markdown=True)
            person.setState(p, 20)
            # state 20
        elif text_input == EN_TEXT_TOFROM_EMOJI:
            randomEmoji = emojiTags.getRandomSingleEmoji(italian=False)
            randomWord = emojiTags.getRandomTag(italian=False)
            tell(p.chat_id, "Please entere a single emoji, for instance " + randomEmoji +
                  ", or one or more English words, for instance '" + randomWord + "'", kb=[[BOTTONE_INDIETRO]])
            person.setState(p, 21)
            # state 21
        elif text_input == BOTTONE_PINOCCHIO and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            redirectToState(p, 30)
        elif text_input == BOTTONE_COSTITUZIONE:
            redirectToState(p, 40)
        elif text_input == BOTTONE_GRAMMATICA:
            redirectToState(p, 10)
        elif text_input == BOTTONE_GIOCA:
            goToGamePanel(p)
            # state 50
        #elif text_input.lower().strip() == FUTURO_REMOTO_COMMAND:
        #   if p.chat_id!=key.FEDE_CHAT_ID:
        #        redirectToState(p, 80)
        #    else:
        #        redirectToState(p, 81)
        elif p.chat_id in key.MASTER_CHAT_ID:
            if text_input == '/test':
                emoji = u'\U0001F1EE\U0001F1F2'
                tell(p.chat_id, emoji.encode('utf-8'))
            elif text_input == '/testUnicode':
                txt = "Questa è una frase con unicode"
                tell(p.chat_id, txt + " " + str(type(txt)))
            elif text_input == '/testTime':
                txt = "Current time: {}".format(date_util.dateTimeString())
                tell(p.chat_id, txt)
            elif text_input.startswith("/getPinocchioEmojiChapterSentence"):
                input_split = text_input.split(' ')
                ch = int(input_split[1].strip())
                line = int(input_split[1].strip())
                sentence = pinocchio.getPinocchioEmojiChapterSentence(ch, line)
                tell(p.chat_id, sentence)
            elif text_input.startswith("/getEmojiCodePoint"):
                input_split = text_input.split(' ')
                e = input_split[1]
                result = emojiUtil.getCodePointUpper(e)
                tell(p.chat_id, result)
            elif text_input == '/glossStats':
                emojiTranslationsCounts = gloss.getEmojiTranslationsCount()
                textMsg = "Emoji and Translations counts: " + str(emojiTranslationsCounts) + "\n"
                textMsg += "Gaps in numbering: " + str(gloss.getNumberingGaps())
                tell(p.chat_id, textMsg)
            elif text_input.startswith('/sendText'):
                dealWithsendTextCommand(p, text_input, markdown=False)
            elif text_input.startswith('/restartUsers'):
                msgTxt = None
                if ' ' in text_input:
                    msgTxt = text_input[text_input.index(' ') + 1:]
                deferred.defer(restartAllUsers, text_input)  # 'New interface :)')
            elif text_input.startswith('/getConfusionWordToEmojis'):
                if ' ' in text_input:
                    d = confusionTables.getConfusionWordToEmojis(text_input[text_input.index(' ') + 1:])
                    textMsg = ""
                    for (k, v) in d.items():
                        textMsg += k.encode('utf-8') + ": " + str(v)
                    tell(p.chat_id, textMsg)
                else:
                    tell(p.chat_id, 'missing text after command')
            elif text_input.startswith('/getConfusionEmojiToWords'):
                if ' ' in text_input:
                    tell(p.chat_id, str(confusionTables.getConfusionEmojiToWords(text_input[text_input.index(' ') + 1:])))
                else:
                    tell(p.chat_id, 'missing text after command')
            elif text_input == '/infocount':
                tell(p.chat_id, getInfoCount(), markdown=True)
            elif text_input.startswith('/broadcast ') and len(text_input) > 11:
                msg = text_input[11:]
                deferred.defer(broadcast, p.chat_id, msg, markdown=True, restart_user=False)
            elif text_input.startswith('/testText '):
                text = text_input.split(' ', 1)[1]
                if text:
                    logging.debug("Test broadcast " + text)
                    tell(p.chat_id, text, markdown=True)
            elif text_input.startswith('/restartBroadcast ') and len(text_input) > 18:
                msg = text_input[18:]
                deferred.defer(broadcast, p.chat_id, msg, restart_user=True)
            else:
                tell(p.chat_id, 'Scusa, capisco solo /help /start '
                                'e altri comandi segreti...')
        else:
            tell(p.chat_id,
                 "Scusa non capisco quello che hai detto.\n"
                 "Usa i pulsanti sotto o premi /help per avere informazioni.")

def dealWithsendTextCommand(p, sendTextCommand, markdown=False):
    split = sendTextCommand.split()
    if len(split) < 3:
        tell(p.chat_id, 'Commands should have at least 2 spaces')
        return
    if not split[1].isdigit():
        tell(p.chat_id, 'Second argumnet should be a valid chat_id')
        return
    id = int(split[1])
    sendTextCommand = ' '.join(split[2:])
    if tell_person(id, sendTextCommand, markdown=markdown):
        user = person.getPersonByChatId(id)
        tell(p.chat_id, 'Successfully sent text to ' + user.getFirstName())
    else:
        tell(p.chat_id, 'Problems in sending text')

# ================================
# GO TO STATE 10: PINOCCHIO GRAMMATICA
# ================================

def goToState10(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    COMMANDS = grammar_rules.COMMANDS
    kb = utility.distributeElementMaxSize([str(x) for x in range(1, len(COMMANDS) + 1)])
    kb.append([BOTTONE_INDIETRO])
    if giveInstruction:
        msg = grammar_rules.GRAMMAR_INSTRUCTIONS
        tell(p.chat_id, msg, kb, markdown=True)
    else:
        if text_input == BOTTONE_INDIETRO:
            restart(p)
        elif text_input == LISTA_REGOLE_BUTTON:
            repeatState(p)
        else:
            if text_input.startswith('/'):
                numberStr = text_input[1:]
            else:
                numberStr = text_input
            if utility.representsIntBetween(numberStr, 1, len(COMMANDS)):
                position = int(numberStr)
                msg = grammar_rules.getGrammarRulesText(position)
                kb = [[LISTA_REGOLE_BUTTON], [BOTTONE_INDIETRO]]
                tell(p.chat_id, msg, kb, markdown=True)
            else:
                tell(p.chat_id, "Input non valido.")

# ================================
# GO TO STATE 30: PINOCCHIO
# ================================

def goToState30(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        kb = [
            [BOTTONE_GLOSSARIO],
            [LEGGGI_PINOCCHIO_BUTTON],
            [BOTTONE_INDIETRO]
        ]
        msg = "(Area riservata) Premi uno dei pulsanti per entrare nel mondo di PINOCCHIO."
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            restart(p)
        elif text_input == BOTTONE_GLOSSARIO and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            redirectToState(p, 310)
        elif text_input == LEGGGI_PINOCCHIO_BUTTON and p.chat_id in key.GLOSS_ACCESS_CHAT_ID:
            redirectToState(p, 330)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco")

# ================================
# GO TO STATE 310: GLOSSARIO PINOCCHIO
# ================================

def goToState310(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        kb=[[INSERIRE_GLOSSARIO_BUTTON, ELIMINARE_GLOSSARIO_BUTTON],[BOTTONE_INDIETRO]]
        msg = "Vuoi {} o {} una voce nel glossario?".format(INSERIRE_GLOSSARIO_BUTTON, ELIMINARE_GLOSSARIO_BUTTON)
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            redirectToState(p, 30)
        elif text_input == INSERIRE_GLOSSARIO_BUTTON:
            p.tmpString = None
            redirectToState(p, 311)
        elif text_input == ELIMINARE_GLOSSARIO_BUTTON:
            redirectToState(p, 312)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco")

# ================================
# GO TO STATE 311: GLOSSARIO PINOCCHIO - INSERIRE VOCE
# ================================

def goToState311(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        p.resetTmpStrIfNotNone()
        kb = [[BOTTONE_INDIETRO]]
        msg = INSERISCI_ELIMINA_VOCE_TEXT('INSERISCI')
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            redirectToState(p, 310)
        else:
            if p.tmpString:
                if text_input == BOTTONE_SI:
                    text_input = p.tmpString.encode('utf-8')
                elif text_input == BOTTONE_NO:
                    tell(p.chat_id, "Inserimento Annullato.")
                    redirectToState(p, 310)
                    return
                else:
                    tell(p.chat_id, FROWNING_FACE + " Scusa non capisco quello che hai detto, capisco solo SI o NO.")
                    return
            else:
                text_input = text_input.strip()
            split = text_input.split('|')
            if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0:
                word = split[1].strip()
                emoji = split[0].replace(' ', '')
                emojiNorm = emojiUtil.normalizeEmojiText(emoji)
                if emoji == emojiNorm:
                    present_emojis = gloss.getEmojiListFromText(word)
                    txtMsg = ''
                    if present_emojis:
                        if emoji in present_emojis:
                            txtMsg = "{} L'emoji {} è già associato al testo '{}'".format(CANCEL, emoji, word)
                            tell(p.chat_id, txtMsg)
                            repeatState(p)
                            return
                        present_emoji_str = ', '.join(present_emojis)
                        txtMsg += "{} Omonimia! Parola già presente nel glossario " \
                                  "associata a questo/i emoji: {}\n\n".format(EXCLAMATION, present_emoji_str)
                    sendGlossarioNotification(p, True, text_input)
                    present_gloss = gloss.getGlossFromEmoji(emoji)
                    if present_gloss:
                        gloss.appendTargetText(p, present_gloss, word)
                        present_words = present_gloss.target_text
                        words = [x.encode('utf-8') for x in present_words]
                        txtMsg += "{} Voce aggiornata nel glossario: " \
                                  "{}|{}\nGrazie! {}".format(CHECK, emoji, ', '.join(words),CLAPPING_HANDS)
                        tell(p.chat_id, txtMsg)
                        repeatState(p)
                    else:
                        gloss.addGloss(p, emoji, word)
                        txtMsg += "{} Voce inserita nel glossario, grazie! {}".format(CHECK, CLAPPING_HANDS)
                        tell(p.chat_id, txtMsg)
                        repeatState(p)
                elif emojiNorm:
                    emojiNorm_word = emojiNorm + "|" + word
                    txtMsg = CONFIRM_NORM_TEXT(emojiNorm_word)
                    tell(p.chat_id, txtMsg, kb=[[BOTTONE_SI, BOTTONE_NO]])
                    p.setTmpStr(emojiNorm_word)
                else:
                    txtMsg = CANCEL + " Input non valido."
                    tell(p.chat_id, txtMsg)
                    repeatState(p)
            else:
                txtMsg = CANCEL + " Input non valido."
                tell(p.chat_id, txtMsg)
                repeatState(p)

# ================================
# GO TO STATE 312: GLOSSARIO PINOCCHIO - ELIMINARE VOCE
# ================================


def goToState312(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        p.resetTmpStrIfNotNone()
        kb = [[BOTTONE_INDIETRO]]
        msg = INSERISCI_ELIMINA_VOCE_TEXT('ELIMINA')
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            redirectToState(p, 310)
        else:
            if p.tmpString:
                if text_input == BOTTONE_SI:
                    text_input = p.tmpString.encode('utf-8')
                elif text_input == BOTTONE_NO:
                    tell(p.chat_id, "Eliminazione Annullata.")
                    redirectToState(p, 310)
                    return
                else:
                    tell(p.chat_id, FROWNING_FACE + " Scusa non capisco quello che hai detto, capisco solo SI o NO.")
                    return
            else:
                text_input = text_input.strip()
            split = text_input.split('|')
            logging.debug("Split: {}".format(split))
            if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0:
                word = split[1].strip()
                emoji = split[0].replace(' ', '')
                emojiNorm = emojiUtil.normalizeEmojiText(emoji)
                if emojiNorm == emoji:
                    present_gloss = gloss.getGloss(emoji, word)
                    if present_gloss:
                        sendGlossarioNotification(p, False, text_input)
                        if len(present_gloss.target_text) == 1:
                            gloss.deleteGloss(present_gloss)
                            txtMsg = CHECK + " Voce eliminata dal glossario, grazie! " + CLAPPING_HANDS
                            tell(p.chat_id, txtMsg)
                            repeatState(p)
                        else:
                            if gloss.deleteEntry(p, present_gloss, word):
                                present_words = present_gloss.target_text
                                words = [x.encode('utf-8') for x in present_words]
                                txtMsg = "{} Voce eliminata dal glossario!\n" \
                                         "L'emoji {} rimane associato alle seguenti parole: {}".format(CHECK, emoji, ', '.join(words))
                                tell(p.chat_id, txtMsg)
                                repeatState(p)
                            else:
                                txtMsg = '❗❗ Non riesco ad eliminare questa voce, ti prego di contattare @kercos.'
                                tell(p.chat_id, txtMsg)
                                redirectToState(p, 310)
                    else:
                        txtMsg = CANCEL + " Voce non presente nel glossario."
                        tell(p.chat_id, txtMsg)
                        repeatState(p)
                elif emojiNorm:
                    emojiNorm_word = emojiNorm + "|" + word
                    txtMsg = CONFIRM_NORM_TEXT(emojiNorm_word)
                    tell(p.chat_id, txtMsg, kb=[[BOTTONE_SI, BOTTONE_NO]])
                    p.setTmpStr(emojiNorm_word)
                else:
                    txtMsg = CANCEL + " Input non valido."
                    tell(p.chat_id, txtMsg)
                    repeatState(p)
            else:
                txtMsg = CANCEL + " Input non valido."
                tell(p.chat_id, txtMsg)
                repeatState(p)

# ================================
# GO TO STATE 330: LGEGI PINOCCHIO
# ================================

def goToState330(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    sentenceIdString = p.getPinocchioSentenceIndex()
    if giveInstruction:
        kb = [[PREV_BUTTON, NEXT_BUTTON],[BOTTONE_INDIETRO]]
        msg = pinocchio.getSentenceEmojiString(sentenceIdString)
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            redirectToState(p, 30)
        elif text_input == PREV_BUTTON:
            prevSentenceIndex = pinocchio.getPrevChapterLineIndex(sentenceIdString)
            if prevSentenceIndex:
                p.setPinocchioSentenceIndex(prevSentenceIndex)
                repeatState(p)
            else:
                tell(p.chat_id, "❗  Hai raggiunto l'inizio del libro.")
                repeatState(p)
        elif text_input == NEXT_BUTTON:
            nextSentenceIndex = pinocchio.getNextChapterLineIndex(sentenceIdString)
            if nextSentenceIndex:
                p.setPinocchioSentenceIndex(nextSentenceIndex)
                repeatState(p)
            else:
                tell(p.chat_id, "❗  Hai raggiunto la fine del libro.")
                repeatState(p)
        elif ':' in text_input:
            if pinocchio.isValidChLineIndexStr(text_input):
                p.setPinocchioSentenceIndex(text_input)
                repeatState(p)
            else:
                tell(p.chat_id, "Frase non trovata. Se vuoi andare alla frase 3 del capitolo 1 inserisci 1:3")
        else:
            tell(p.chat_id, "Input non valido. Se vuoi andare alla frase 3 del capitolo 1 inserisci 1:3")


# ================================
# GO TO STATE 40: LEGGI COSTITUZIONE
# ================================

index_array = utility.distributeElementMaxSize(['/Art_{}'.format(x) for x in range(1,13)],4)

COSTITUZIONE_INDICE = "📜🇮🇹 Costituzione italiana\n\n" \
                      "	_☝️️📃_🔝_☝️️📃_🔝 Principi fondamentali\n" + \
                      '\n'.join(' '.join(line) for line in index_array) + \
                      "\n\n(N.B. La Costituzione in emojitaliano è suscettibile di revisione)"

def goToState40(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    sentenceId = p.costituzioneSentenceIndex
    if giveInstruction:
        kb = [[PREV_BUTTON, NEXT_BUTTON],[BOTTONE_INDICE],[BOTTONE_INDIETRO]]
        if sentenceId == "0:0:0":
            msg = COSTITUZIONE_INDICE
        else:
            msg = costituzione.getSentenceEmojiString(sentenceId)
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            restart(p)
        elif text_input == PREV_BUTTON:
            prevSentenceIndex = costituzione.getPrevSentenceId(sentenceId)
            if prevSentenceIndex:
                p.setCostituzioneSentenceIndex(prevSentenceIndex)
                repeatState(p)
            else:
                tell(p.chat_id, "❗  Hai raggiunto l'inizio.")
                repeatState(p)
        elif text_input == NEXT_BUTTON:
            nextSentenceIndex = costituzione.getNextSentenceId(sentenceId)
            if nextSentenceIndex:
                p.setCostituzioneSentenceIndex(nextSentenceIndex)
                repeatState(p)
            else:
                tell(p.chat_id, "❗  Hai raggiunto la fine.")
                repeatState(p)
        elif text_input == BOTTONE_INDICE:
            p.setCostituzioneSentenceIndex("0:0:0")
            repeatState(p)
        elif text_input.startswith('/Art_'):
            art_number = text_input[5:]
            if utility.representsIntBetween(art_number,1,12):
                art_number = int(art_number)
                p.setCostituzioneSentenceIndex('1:{}:1'.format(art_number))
                repeatState(p)
            else:
                tell(p.chat_id, "Input non valido.")
        else:
            tell(p.chat_id, "Input non valido.")

# ================================
# aux functions
# ================================

def goToGamePanel(p):
    msg = utility.unindent(
        """
        Abbiamo due semplici giochi attivi: \
        puoi indovinare un emoji a partire da una parola ({}) \
        oppure viceversa ({})
        """.format(IT_TO_EMOJI, EMOJI_TO_IT)
    )
    kb = [[IT_TO_EMOJI, EMOJI_TO_IT], [BOTTONE_INDIETRO]]
    if FUTURO_REMOTO_ON:
        kb.insert(1, [BUTTON_FUTURO_REMOTO])
    tell(p.chat_id, msg, kb)
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

# ================================
# GO TO STATE 80: FUTURO REMOTO
# ================================

def goToState80(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    quizOpen = quizGame.isQuizOpen()
    quizAdmin = quizGame.getQuizAdminId() if quizOpen else None
    if giveInstruction:
        msg = utility.unindent(
            """
            Benvenuto/a Futuro Remoto!
            Da questa schermata potrai accedere al quiz di Futuro Remoto!
            Qua sotto troverai il pulsante {} quando il QUIZ verrà aperto; se vuoi aggiornare la schermata premi su {}.
            """.format(BUTTON_QUIZ, BUTTON_REFRESH)
        )
        kb = [[BOTTONE_INDIETRO]]
        if quizOpen:
            kb.insert(0, [BUTTON_QUIZ])
        elif p.isAdmin():
            kb.insert(0, [BUTTON_START_QUIZ])
            msg = "Premi su {} se vuoi iniziare il quiz.".format(BUTTON_START_QUIZ)
        else:
            kb.insert(0, [BUTTON_REFRESH])
        tell(p.chat_id, msg, kb)
    else:
        if text_input == BOTTONE_INDIETRO:
            restart(p)
        elif text_input == BUTTON_REFRESH:
            repeatState(p)
        elif text_input == BUTTON_START_QUIZ and p.isAdmin():
            if quizGame.isQuizOpen():
                if quizAdmin == p.chat_id:
                    redirectToState(p, 82)
                else:
                    msg = 'Il quiz è già stato attivato da {}\n' \
                          'Sei entrato/a come partecipante'.format(quizGame.getQuizAdminName())
                    tell(p.chat_id, msg)
                    redirectToState(p, 80)
            else:
                quizGame.startQuiz(p.chat_id)
                redirectToState(p, 82)
        elif text_input == BUTTON_QUIZ:
            if quizGame.isQuizOpen():
                if quizAdmin == p.chat_id:
                    msg = 'Sei di nuovo nel quiz come amministratore'
                    tell(p.chat_id, msg)
                    redirectToState(p, 82)
                else:
                    redirectToState(p, 81)
            else:
                msg = 'Il quiz non è più attivo'
                tell(p.chat_id, msg)
                repeatState(p)
        else:
            tell(p.chat_id, FROWNING_FACE + " Scusa, non capisco.")

# ================================
# GO TO STATE 81: Futuro Remoto Participants
# ================================
ANSWER_BUTTONS = ['A','B','C','D']

def goToState81(p, text_input=None, **kwargs):
    giveInstruction = text_input is None
    if giveInstruction:
        msg = "Ciao {}, benvenuto/a al quiz di Emojitaliano!".format(p.getFirstName())
        kb = [ANSWER_BUTTONS]
        tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
    else:
        message_timestamp = kwargs['message_timestamp']
        if text_input in ANSWER_BUTTONS:
            #tell(p.chat_id, "You sent the message at: {}".format(message_timestamp))
            questionNumber, ellapsedSeconds = quizGame.addAnswer(p, text_input, message_timestamp)
            if ellapsedSeconds == -1:
                # answers are not currently accepted
                msg = FROWNING_FACE + ' Mi dispiace, le risposte sono bloccate in questo momento.'
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
            elif ellapsedSeconds == -2:
                # user already answered to the question
                msg = FROWNING_FACE + ' Mi dispiace, hai già risposto alla domanda numero {}.'.format(questionNumber)
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
            else: # >0
                msg = utility.unindent(
                    """
                    Grazie!  😊
                    Hai risposto in {} secondi.
                    La tua risposta ({}) alla domanda {} è stata registrata.
                    """.format(ellapsedSeconds, text_input, questionNumber)
                )
                tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        else:
            tell(p.chat_id, FROWNING_FACE + " Mi dispiace, non capisco. Premi su A, B, C o D.")

# ================================
# GO TO STATE 82: Futuro Remoto ADMIN
# ================================

def goToState82(p, text_input=None, **kwargs):
    NEXT_QUESTION_BUTTON = 'PROSSIMA DOMANDA'
    STOP_ANSWERS_BUTTON = 'STOP RISPOSTE'
    END_QUIZ_BUTTON = 'FINE QUIZ'
    PEOPLE_IN_QUIZ_BUTTON = 'PERSONE NEL QUIZ'
    GLOBAL_STATS_BUTTON = 'GLOBAL STATS'
    RESTART_QUIZ_BUTTON = 'RESTART QUIZ'
    WINNING_MSG = [
        "🎉🎉🎉 CONGRATULAZIONI, HAI VINTO IL QUIZ!\nVIENI A RITIRARE IL TUO PREMIO!  🎉🎉🎉",
        "🎉🎉🎉 CONGRATULAZIONI, HAI VINTO IL 2° POSTO!\nVIENI A RITIRARE IL TUO PREMIO! 🎉🎉🎉",
        "🎉🎉🎉 CONGRATULAZIONI, HAI VINTO IL 3° POSTO!\nVIENI A RITIRARE IL TUO PREMIO! 🎉🎉🎉",
    ]
    giveInstruction = text_input is None
    if giveInstruction:
        kb = [
            [NEXT_QUESTION_BUTTON],
            [PEOPLE_IN_QUIZ_BUTTON, GLOBAL_STATS_BUTTON],
            [END_QUIZ_BUTTON, RESTART_QUIZ_BUTTON]
        ]
        msg = "Sei l'amministratore del quiz!"
        tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
    else:
        if text_input == END_QUIZ_BUTTON:
            userAnswersTable = quizGame.getUserAnswersTable()
            firstN_chat_id, summary = quizGame.getUserAnswersTableSorted(3)
            tell(p.chat_id, summary, sleepDelay=True, one_time_keyboard=False)
            enuList = list(enumerate(firstN_chat_id))
            deferred.defer(broadcast_quiz_final_msg, p.chat_id, 81, userAnswersTable, restart_user=True)
            sleep(3)
            for i, id in enuList:
                tell(id, WINNING_MSG[i])
            sleep(1)
            quizGame.stopQuiz()
            restart(p)
        elif text_input == PEOPLE_IN_QUIZ_BUTTON:
            c = person.getPeopleCountInState(81)
            msg = 'Ci sono {} persone nel quiz.'.format(c)
            tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        elif text_input == RESTART_QUIZ_BUTTON:
            quizGame.startQuiz(p.chat_id)
            msg = 'Il quiz è stato resettato.'
            tell(p.chat_id, msg, sleepDelay=True, one_time_keyboard=False)
        elif text_input == NEXT_QUESTION_BUTTON:
            quizGame.addQuestion()
            kb = [[STOP_ANSWERS_BUTTON]]
            msg = 'Fai la domanda (a voce) e quando vuoi bloccare le risposte premi su {}.'.format(STOP_ANSWERS_BUTTON)
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif text_input == STOP_ANSWERS_BUTTON:
            quizGame.stopAcceptingAnswers()
            kb = [ANSWER_BUTTONS]
            msg = 'Le risposte sono state bloccate. Inserisci la risposta corretta.'
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif text_input in ANSWER_BUTTONS:
            correctNamesTimeSorted = quizGame.validateAnswers(text_input)
            correctNamesStr = ', '.join([x for x in correctNamesTimeSorted])
            msg = 'Le risposte sono state controllate. \n' \
                  "Le persone che hanno risposto correttamente all'ultima domanda sono {}: {}".format(
                len(correctNamesTimeSorted), str(correctNamesStr))
            kb = [
                [NEXT_QUESTION_BUTTON],
                [PEOPLE_IN_QUIZ_BUTTON, GLOBAL_STATS_BUTTON],
                [END_QUIZ_BUTTON, RESTART_QUIZ_BUTTON]
            ]
            tell(p.chat_id, msg, kb, sleepDelay=True, one_time_keyboard=False)
        elif text_input == GLOBAL_STATS_BUTTON:
            firstN_chat_id, summary = quizGame.getUserAnswersTableSorted()
            tell(p.chat_id, summary, sleepDelay=True, one_time_keyboard=False)
        else:
            tell(p.chat_id, FROWNING_FACE + "Mi dispiace, non capisco")

def broadcast_quiz_final_msg(sender_id, state, userAnswersTable, restart_user=False, markdown=False, curs=None):
    users, next_curs, more = Person.query(Person.state == state).fetch_page(50, start_cursor=curs)
    try:
        for p in users:
            if p.enabled:
                if restart_user:
                    restart(p)
                score, ellapsed = quizGame.getUserScoreEllapsed(p, userAnswersTable)
                if score == 0:
                    msg = "Hai risposto correttamente a 0 domande."
                else:
                    msg = utility.unindent(
                        """
                        Hai risposto correttamente a {} domande in {} secondi complessivi.
                        Grazie per aver partecipato al quiz!
                        """.format(score, ellapsed)
                    )
                tell(p.chat_id, msg, sleepDelay=True)
    except datastore_errors.Timeout:
        sleep(1)
        deferred.defer(broadcast_quiz_final_msg, sender_id, state, userAnswersTable, restart_user, markdown, curs)
        return
    if more:
        deferred.defer(broadcast_quiz_final_msg, sender_id, state, userAnswersTable, restart_user, markdown, next_curs)
    else:
        msg_debug = "Il messaggio finale è stato inviato ai partecipanti."
        tell(sender_id, msg_debug)

# ================================
# ================================
# ================================


def getEmojiListFromTagInDictAndGloss(string):
    result = set()
    emojiList = emojiTags.getEmojisForTag(string)
    if emojiList:
        result.update([tag_emoji for tag_emoji in emojiList])
    gloss_emoji_list = gloss.getEmojiListFromText(string)
    if gloss_emoji_list:
        result.update([gloss_emoji for gloss_emoji in gloss_emoji_list])
    return list(result)

def getEmojiFromString(input_string, italian=True, pinocchioSearch=False):

    if emojiUtil.stringContainsAnyStandardEmoji(input_string):
        if italian:
            msg = EXCLAMATION + " Il testo inserito deve contenere solo emoji o solo lettere.\n"
        else:
            msg = EXCLAMATION + " The inserted text should contain only emoji or only alphabetic characters.\n"
        return msg

    gloss_emoji_list = gloss.getEmojiListFromText(input_string)

    msg = []
    emojiList = emojiTags.getEmojisForTag(input_string, italian)

    if italian:
        found = False
        if gloss_emoji_list:
            found = True
            gloss_emoji_list_str = ', '.join(gloss_emoji_list)
            msg.append('Trovata voce nel glossario: ' + input_string + " = " + gloss_emoji_list_str)
        if emojiList:
            found = True
            emojisListStr = ', '.join(set(emojiList))
            msg.append('Trovati emoji in tabella unicode con questo tag: ' + emojisListStr)
        if pinocchioSearch:
            index_list = pinocchio.findTextInPinocchio(input_string)
            if index_list:
                found = True
            msg.append('Occorrenze in Pinocchio: ' + ' '.join(index_list))
        if not found:
            msg.append("Nessun emoji trovato per la stringa inserita")
    else:
        if emojiList:
            emojisListStr = ', '.join(set(emojiList))
            msg.append('Found the following emojis in the unicode table with the given tag: ' + emojisListStr)
        else:
            msg.append("No emoji has been found that matches the text_input text.")

    return '\n'.join(msg)



def getStringFromEmoji(input_emoji, italian=True, pinocchioSearch=False, normalization_warning=False):

    emojiNorm = emojiUtil.normalizeEmojiText(input_emoji)
    if emojiNorm != input_emoji:
        if emojiNorm:
            result = getStringFromEmoji(emojiNorm, italian, pinocchioSearch, normalization_warning)
            if normalization_warning:
                if italian:
                    return EXCLAMATION + "Emoji normalizzato: {}\n\n{}".format(emojiNorm, result)
                else:
                    return EXCLAMATION + "Normalized emoji: {}\n\n{}".format(emojiNorm, result)
            else:
                return result
        else:
            if italian:
                return EXCLAMATION + " Il testo inserito deve contenere solo emoji o solo lettere.\n"
            else:
                return EXCLAMATION + " The inserted text should contain only emoji or only alphabetic characters.\n"

    tags = emojiTags.getTagsForEmoji(input_emoji, italian)
    found = False

    msg = []

    if italian:
        gloss_text = gloss.getTextFromEmoji(input_emoji)
        if gloss_text:
            found = True
            words = ', '.join([x.encode('utf-8') for x in gloss_text])
            msg.append('Trovata voce nel glossario: ' + input_emoji + " = " + words)
        if pinocchioSearch:
            index_list = pinocchio.findEmojiInPinocchio(input_emoji)
            if index_list:
                found = True
            msg.append('Occorrenze in Pinocchio: ' + ' '.join(index_list))
            index_list = pinocchio.findEmojiInPinocchio(input_emoji, deepSearch=True)
            if index_list:
                found = True
            msg.append('Occorrenze in Pinocchio (deep search): ' + ' '.join(index_list))
        if tags:
            found = True
            annotations = ', '.join(tags)
            msg.append("Trovato emoji in tabella unicode con questi tags: " + annotations)
        if not found:
            msg.append("L'emoji inserito non è presente nel glossario o nella tabella unicode.")
    else:
        if tags:
            # found = True
            annotations = ', '.join(tags)
            msg.append("Found emoji in unicode table with the following tags: " + annotations)
        # description = emojiUtil.getDescriptionForEmoji(input_emoji)
        # if description:
        #     msg.append("and the following description (identification string): " + description)
        # if not found:
        #     msg.append("The emoji you have inserted is not present in the unicode table.")

    return '\n'.join(msg)

# ================================
# INLINE QUERY
# ================================

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
            numberOfEmoijs = emojiUtil.getNumberOfEmojisInString(e)
            emoji_for_thumb = e if numberOfEmoijs==1 else '🏃‍♂️'
            thumb_url = emojiUtil.getEmojiImageDataFromUrl(emoji_for_thumb)
            if thumb_url == None:
                continue
            result.append(
                {
                    'type': "article",
                    'id': str(id) + '/' + str(i),
                    'title': e,
                    'message_text': msg,
                    'hide_url': True,
                    'thumb_url': thumb_url,
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
        resp = urllib2.urlopen(TELEGRAM_API_BASE_URL + 'answerInlineQuery',
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

class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        allowed_updates = ["message","inline_query", "chosen_inline_result", "callback_query"]
        data = {
            'url': key.TELEGRAM_WEBHOOK_URL,
            'allowed_updates': json.dumps(allowed_updates),
        }
        resp = requests.post(key.TELEGRAM_API_BASE_URL + 'setWebhook', data)
        logging.info('SetWebhook Response: {}'.format(resp.text))
        self.response.write(resp.text)

class GetWebhookInfo(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        resp = requests.post(key.TELEGRAM_API_BASE_URL + 'getWebhookInfo')
        logging.info('GetWebhookInfo Response: {}'.format(resp.text))
        self.response.write(resp.text)

class DeleteWebhook(webapp2.RequestHandler):
    def get(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        resp = requests.post(key.TELEGRAM_API_BASE_URL + 'deleteWebhook')
        logging.info('DeleteWebhook Response: {}'.format(resp.text))
        self.response.write(resp.text)

class InfouserAllHandler(webapp2.RequestHandler):
    def get(self):
        msg = getInfoCount()
        #broadcast(key.FEDE_CHAT_ID, msg, markdown=True)
        tell(key.FEDE_CHAT_ID, msg, markdown=True)

class BroadcastEmojiItalian(webapp2.RequestHandler):
    def get(self):
        from main_twitter import tweet_message
        for _ in range(3):
            randomGlossMultiEmoji = gloss.getRandomGlossMultiEmoji()
            randomGlossMultiEmoji_emoji = randomGlossMultiEmoji.getEmoji()
            randomGlossMultiEmoji_translation = randomGlossMultiEmoji.getFirstTranslation()        
            msg = 'La traduzione di {} da #emojitaliano in italiano è "{}"'.format(randomGlossMultiEmoji_emoji, randomGlossMultiEmoji_translation)
            logging.debug("Broadcast Emoji->Italian: {}".format(msg))
            tweet_message(msg)
            tell_emojitalia_group(msg)
            sleep(2)

class BroadcastQuizTime(webapp2.RequestHandler):
    def get(self):        
        from main_twitter import tweet_message        
        for _ in range(3):
            randomGlossMultiEmoji = gloss.getRandomGlossMultiEmoji()
            randomGlossMultiEmoji_emoji = randomGlossMultiEmoji.getEmoji()
            # randomGlossMultiEmoji_translation = randomGlossMultiEmoji.getFirstTranslation()        
            msg = 'Prova a indovinare una possibile traduzione in italiano di {}\n\n#emojitalianoquiz #emojitaliano'.format(randomGlossMultiEmoji_emoji)
            logging.debug("Quiztime: {}".format(msg))
            tweet_message(msg)
            sleep(2)

class BroadcastItalianEmoji(webapp2.RequestHandler):
    def get(self):
        from main_twitter import tweet_message
        for _ in range(3):
            randomGlossMultiEmoji = gloss.getRandomGlossMultiEmoji()
            randomGlossMultiEmoji_emoji = randomGlossMultiEmoji.getEmoji()
            randomGlossMultiEmoji_translation = randomGlossMultiEmoji.getFirstTranslation()        
            msg = 'La traduzione di "{}" in #emojitaliano è {}'.format(randomGlossMultiEmoji_translation, randomGlossMultiEmoji_emoji)
            logging.debug("Broadcast Italian->Emoji: {}".format(msg))
            tweet_message(msg)
            tell_emojitalia_group(msg)
            sleep(2)

# ================================
# ================================
# ================================


class WebhookHandler(webapp2.RequestHandler):

    def post(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.debug('Telegram post request: {}'.format(body))
        #self.response.write(json.dumps(body))

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
            elif p.isAdmin() and re.match(r'^/\d+_\d+$',text):
                ch,line = text[1:].split('_')
                msg = pinocchio.getSentenceEmojiString('{}:{}'.format(ch,line))
                tell(p.chat_id, msg)
            elif p.state == 20:
                # IT <-> EMOJI
                if text == BOTTONE_INDIETRO:
                    restart(p)
                else:
                    ps = p.isAdmin()
                    if ps:
                        reply('Ricerca avanzata in corso...', markdown=False)
                    if utility.has_roman_chars(text):                        
                        emoji = getEmojiFromString(text, italian=True, pinocchioSearch=ps)
                        reply(emoji, kb=[[BOTTONE_INDIETRO]], markdown=False)
                    else:                        
                        string = getStringFromEmoji(text, italian=True, normalization_warning=p.isAdmin(), pinocchioSearch=ps)
                        reply(string, kb = [[BOTTONE_INDIETRO]], markdown=False)
            elif p.state == 21:
                # EN <-> EMOJI
                if text == BOTTONE_INDIETRO:
                    restart(p)
                else:
                    if utility.has_roman_chars(text):
                        emoji = getEmojiFromString(text, italian=False)
                        reply(emoji, kb=[[BOTTONE_INDIETRO]], markdown=False)
                    else:
                        string = getStringFromEmoji(text, italian=False)
                        reply(string, kb=[[BOTTONE_INDIETRO]], markdown=False)
            elif p.state == 50:
                #GAME PANEL
                if text == BOTTONE_INDIETRO:
                    restart(p)
                    #state 0
                elif text==IT_TO_EMOJI:
                    playWordToEmoji(p)
                    # state 81
                elif text==EMOJI_TO_IT:
                    playEmojiToWord(p)
                    # state 52
                elif text == BUTTON_FUTURO_REMOTO and FUTURO_REMOTO_ON:
                    redirectToState(p, 80)
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
                    emojiNorm = emojiUtil.normalizeEmojiText(text)
                    if emojiNorm and emojiNorm != text:
                        text = emojiUtil.normalizeEmojiText(text)
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
                if not dealWithUniversalCommands(p, text_input=text):
                    logging.debug("Sending {} to state {}. Input: '{}'".format(p.getUserInfoString(), p.state, text))
                    repeatState(p, text_input=text, message_timestamp=message_timestamp)


    def handle_exception(self, exception, debug_mode):
        logging.exception(exception)
        tell(key.FEDE_CHAT_ID, "❗ Detected Exception: " + str(exception))

def report_exception():
    import traceback
    msg = "❗ Detected Exception: " + traceback.format_exc()
    tell(key.FEDE_CHAT_ID, msg, markdown=False)
    logging.error(msg)


possibles = globals().copy()
possibles.update(locals())
