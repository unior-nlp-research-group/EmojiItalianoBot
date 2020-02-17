# -*- coding: utf-8 -*-


import webapp2
import key
#import gloss
#import main_telegram
#import main_twitter

app = webapp2.WSGIApplication([
    ('/set_webhook', 'main_telegram.SetWebhookHandler'),
    ('/get_webhook_info', 'main_telegram.GetWebhookInfo'),
    ('/delete_webhook', 'main_telegram.DeleteWebhook'),
    (key.TELEGRAM_WEBHOOK_PATH, 'main_telegram.WebhookHandler'),
    ('/infouser_weekly_all', 'main_telegram.InfouserAllHandler'),
    ('/broadcast_emoji_italian', 'main_telegram.BroadcastEmojiItalian'),
    ('/broadcast_quiztime', 'main_telegram.BroadcastQuizTime'),
    ('/broadcast_italian_emoji', 'main_telegram.BroadcastItalianEmoji'),
    ('/glossario', 'gloss.GlossarioTableHtml'),
    ('/glossario_invertito', 'gloss.GlossarioTableHtmlInverted'),
    (key.TWITTER_WEBHOOK_PATH, 'main_twitter.WebhookHandler')
], debug=True)
