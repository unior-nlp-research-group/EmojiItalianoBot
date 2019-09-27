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
    ('/tweet_morning', 'main_telegram.TweeetMorning'),
    ('/tweet_noon', 'main_telegram.TweeetNoon'),
    ('/tweet_evening', 'main_telegram.TweeetEvening'),
    ('/glossario', 'gloss.GlossarioTableHtml'),
    ('/glossario_invertito', 'gloss.GlossarioTableHtmlInverted'),
    (key.TWITTER_WEBHOOK_PATH, 'main_twitter.WebhookHandler')
], debug=True)
