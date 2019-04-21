
# -*- coding: utf-8 -*-

import webapp2
import twitter
import key
import json
import logging

import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        deal_with_event(body)
        #return ('',200)

    def get(self):
        from google.appengine.api import urlfetch
        urlfetch.set_default_fetch_deadline(60)
        logging.debug("in twitter_webhook_challenger function")
        crc_token = self.request.get('crc_token')
        reponse_json = {
            'response_token': solve_crc_challenge(crc_token),
        }
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.out.write(json.dumps(reponse_json))

api = twitter.Api(consumer_key=key.TWITTER_CUSUMER_API_KEY,
                  consumer_secret=key.TWITTER_CUSUMER_API_SECRET,
                  access_token_key=key.TWITTER_ACCESS_TOKEN,
                  access_token_secret=key.TWITTER_ACCESS_TOKEN_SECRET)
                

'''
# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#post-account-activity-all-env-name-webhooks
# ok
def set_webhook():    
    from TwitterAPI import TwitterAPI
    twAPI = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )
    r = twAPI.request(
        'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME), 
        {'url': key.WEBHOOK_TWITTER_BASE},
        method_override='POST'
    )
    #id = r.json()['id']
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#get-account-activity-all-env-name-webhooks
# ok
def get_webhook_info():
    from TwitterAPI import TwitterAPI
    twAPI = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )
    r = twAPI.request(
        'account_activity/all/:{}/webhooks'.format(key.TWITTER_ENVNAME), 
        method_override='GET'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#put-account-activity-all-env-name-webhooks-webhook-id
# ok
def trigger_CRC_request():
    from TwitterAPI import TwitterAPI
    twAPI = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )
    r = twAPI.request(
        'account_activity/all/:{}/webhooks/:{}'.format(key.TWITTER_ENVNAME, 1066955205047173120), 
        method_override='PUT'
    )
    return r.text

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#post-account-activity-all-env-name-subscriptions
# ok (after resetting permission in twitter console)
def add_user_subscription():
    from TwitterAPI import TwitterAPI
    twAPI = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )
    r = twAPI.request(
        'account_activity/all/:{}/subscriptions'.format(key.TWITTER_ENVNAME), 
        method_override='POST'
    )
    return r.text


# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#get-account-activity-all-env-name-subscriptions
def get_user_subscription():
    r = api.request(
        'account_activity/all/:{}/subscriptions'.format(key.TWITTER_ENVNAME), 
        method_override='GET'
    )
    return r.text

def post_retweet(message_text, original_tweet_id=None):
    if original_tweet_id:
        r = api.request('statuses/update', {'status': message_text, 'in_reply_to_status_id':original_tweet_id})        
    else:
        r = api.request('statuses/update', {'status': message_text})
    print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)

''' 

# https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/api-reference/aaa-premium#put-account-activity-all-env-name-webhooks-webhook-id
# ok
def trigger_CRC_request():    
    from TwitterAPI import TwitterAPI
    twAPI = TwitterAPI(
        key.TWITTER_CUSUMER_API_KEY, key.TWITTER_CUSUMER_API_SECRET,
        key.TWITTER_ACCESS_TOKEN, key.TWITTER_ACCESS_TOKEN_SECRET
    )
    r = twAPI.request(
        'account_activity/all/:{}/webhooks/:{}'.format(key.TWITTER_ENVNAME, 1066955205047173120), 
        method_override='PUT'
    )
    return r.text

def solve_crc_challenge(crc_token):
    # https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/securing-webhooks.html
    # https://developer.twitter.com/en/docs/accounts-and-users/subscribe-account-activity/guides/getting-started-with-webhooks
    import base64
    import hashlib
    import hmac   

    # creates HMAC SHA-256 hash from incomming token and your consumer secret
    sha256_hash_digest = hmac.new(
        key.TWITTER_CUSUMER_API_SECRET.encode('utf-8'), 
        msg=crc_token.encode('utf-8'), 
        digestmod=hashlib.sha256
    ).digest()

    return 'sha256=' + base64.b64encode(sha256_hash_digest).decode('utf-8')

def test():
    api.PostDirectMessage(user_id=key.TWITTER_FEDE_ID, text='test')    

def get_user_info(key, value):
    assert key in ['user_id', 'screen_name']
    if key=='user_id':
        user = api.GetUser(user_id=value)
    else:
        user = api.GetUser(screen_name=value)
    if user:
        return {
            'user_id': user.id,
            'screen_name': user.screen_name,
            'name': user.name,
        }
    return {}


def deal_with_event(event_json):
    if 'direct_message_events' in event_json:
        process_direct_message(event_json)
    elif 'tweet_create_events' in event_json:
        process_tweet_post(event_json)                

def build_response(text_input):    
    import gloss
    import emojiUtil
    from utility import has_roman_chars    
    logging.debug('input text type: {}'.format(type(text_input)))
    if has_roman_chars(text_input):
        # text -> emoji        
        translation_list = gloss.getEmojiListFromText(text_input)
        translation_str = ', '.join(translation_list)
        if translation_str:
                if len(translation_list)==1:
                    return 'La traduzione di "{}" in #emojitaliano è {}'.format(text_input, translation_str)
                else:
                    return 'Le possibili traduzioni di "{}" in #emojitaliano sono: {}'.format(text_input, translation_str)
    else:
        # emoji -> text      
        text_input = emojiUtil.normalizeEmojiText(text_input)  
        translation_list = gloss.getTextFromEmoji(text_input)
        translation_str = ', '.join([x.encode('utf-8') for x in translation_list])            
        if translation_str:
                if len(translation_list)==1:
                    return "La traduzione di {} da #emojitaliano è {}".format(text_input, translation_str)
                else:
                    return "Le possibili traduzioni di {} da #emojitaliano sono: {}".format(text_input, translation_str)
    return None

def process_direct_message(event_json):
    message_info = event_json['direct_message_events'][0]['message_create']
    sender_id = message_info['sender_id']    
    if sender_id != key.TWITTER_BOT_ID:
        logging.debug("TWITTER DIRECT MESSAGE: {}".format(json.dumps(event_json)))        
        sender_screen_name = event_json['users'][sender_id]['screen_name']
        #sender_name = get_user_info('user_id', sender_id).get('name', None)
        message_text = message_info['message_data']['text'].encode('utf-8')
        reply_text = build_response(message_text)
        logging.debug('TWITTER Reply to direct message from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))        
        if reply_text:
            api.PostDirectMessage(user_id=sender_id, text=reply_text)

def process_tweet_post(event_json): 
    import re   
    tweet_info = event_json['tweet_create_events'][0]
    if 'retweeted_status' in tweet_info:
        logging.debug('Retweet detected')
        return
    message_text = tweet_info['text'].encode('utf-8')
    user_info = tweet_info['user']
    sender_screen_name = user_info['screen_name']
    #mentions_screen_name = [
    #    x['screen_name'] 
    #    for x in tweet_info['entities']['user_mentions'] 
    #    if x['screen_name']!=key.TWITTER_BOT_SCREEN_NAME
    #]
    if sender_screen_name != key.TWITTER_BOT_SCREEN_NAME:  
        logging.debug("TWITTER POST REQUEST: {}".format(json.dumps(event_json)))        
        message_text = re.sub(r'(#|@)\w+','',message_text).strip()        
        reply_text = build_response(message_text)
        if reply_text:            
            #sender_id = user_info['id']
            #sender_name = user_info['name']        
            tweet_id = int(tweet_info['id'])
            #if mentions_screen_name:
            #        reply_text += ' ' + ' '.join(['@{}'.format(x) for x in mentions_screen_name])                        
            logging.debug('TWITTER Reply to direct message from @{} with text {} -> {}'.format(sender_screen_name, message_text, reply_text))        
            api.PostUpdate(status=reply_text.decode('utf-8'), in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)            

def daylyTweet(msg):
    api.PostUpdate(status=msg.decode('utf-8'))            