# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import ndb

from gloss import Gloss
import key
import pinocchio_sentence
import costituzione

class Person(ndb.Model):
    chat_id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    last_name = ndb.StringProperty(default='-')
    username = ndb.StringProperty(default='-')
    state = ndb.IntegerProperty(default=-1, indexed=True)
    last_mod = ndb.DateTimeProperty(auto_now=True)
    enabled = ndb.BooleanProperty(default=True)
    glossGame = ndb.StructuredProperty(Gloss)
    tmpInt = ndb.IntegerProperty()
    tmpString = ndb.StringProperty()
    pinocchioSentenceIndex = ndb.StringProperty(default=pinocchio_sentence.getSentenceUniqueId(1, 1))
    costituzioneSentenceIndex = ndb.StringProperty(default=costituzione.getSentenceUniqueId(0,0,0))

    def isAdmin(self):
        return self.chat_id in key.MASTER_CHAT_ID

    def getFirstName(self):
        return self.name.encode('utf-8') if self.name else None


    def getLastName(self):
        return self.last_name.encode('utf-8') if self.last_name else None


    def getUsername(self):
        return self.username.encode('utf-8') if self.username else None

    def getFirstLastName(self):
        result = self.getFirstName()
        if self.last_name:
            result += ' ' + self.getLastName()
        return result

    def getUserInfoString(self):
        info = self.getFirstName()
        if self.last_name:
            info += ' ' + self.getLastName()
        if self.username:
            info += ' @' + self.getUsername()
        info += ' ({0})'.format(str(self.chat_id))
        return info


    def setState(self, newstate, put=True):
        self.last_state = self.state
        self.state = newstate
        if put:
            self.put()

    def setEnabled(self, enabled, put=False):
        self.enabled = enabled
        if put:
            self.put()

    def resetTmpStrIfNotNone(self):
        if self.tmpString != None:
            self.tmpString = None
            self.put()

    def setTmpStr(self, value):
        self.tmpString = value
        self.put()

    def setPinocchioSentenceIndex(self, value):
        self.pinocchioSentenceIndex = value
        self.put()

    def getPinocchioSentenceIndex(self):
        return self.pinocchioSentenceIndex.encode('utf-8')

    def setCostituzioneSentenceIndex(self, value):
        self.costituzioneSentenceIndex = value
        self.put()


def getPersonByChatId(chat_id):
    return Person.get_by_id(str(chat_id))

def addPerson(chat_id, name):
    p = Person(
        id=str(chat_id),
        name=name,
        chat_id=chat_id,
    )
    p.put()
    return p

def setState(p, state):
    p.state = state
    p.put()

def getPeopleCountInState(state):
    return Person.query(Person.state == state).count()

def resetePeople():
    selected_people = Person.query(Person.costituzioneSentenceIndex != None).fetch()
    for p in selected_people:
        p.costituzioneSentenceIndex = costituzione.getSentenceUniqueId(0, 0, 0)
    create_futures = ndb.put_multi_async(selected_people)
    ndb.Future.wait_all(create_futures)