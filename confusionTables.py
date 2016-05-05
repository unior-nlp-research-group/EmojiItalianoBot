

from google.appengine.ext import ndb

class ConfusionEmojiToWord(ndb.Model):
    #id source_emoji
    wordCounts = ndb.PickleProperty(default={})

class ConfusionWordsToEmoji(ndb.Model):
    #id word
    emojiCounts = ndb.PickleProperty(default={})

def addConfusionEmojiToWords(emoji, word):
    confEntry = ConfusionEmojiToWord.get_or_insert(emoji)
    if word in confEntry.wordCounts.keys():
        confEntry.wordCounts[word] += 1
    else:
        confEntry.wordCounts[word] = 1
    confEntry.put()

def addConfusionWordToEmojis(word, emoji):
    confEntry = ConfusionWordsToEmoji.get_or_insert(word)
    if emoji in confEntry.emojiCounts.keys():
        confEntry.emojiCounts[emoji] += 1
    else:
        confEntry.emojiCounts[emoji] = 1
    confEntry.put()

def getConfusionEmojiToWords(emoji):
    confEntry = ConfusionEmojiToWord.get_by_id(emoji)
    if confEntry:
        return confEntry.wordCounts
    return {}

def getConfusionWordToEmojis(word):
    confEntry = ConfusionWordsToEmoji.get_by_id(word)
    if confEntry:
        return confEntry.emojiCounts
    return {}
