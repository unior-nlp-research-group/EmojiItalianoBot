# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import ndb

from gloss import Gloss
import key

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

    def isAdmin(self):
        return self.chat_id in key.MASTER_CHAT_ID

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