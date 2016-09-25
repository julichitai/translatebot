import os
import logging
import telebot
from flask import Flask,request
import requests
import re
from telebot import types
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG, filename = u'mylogtest.log')


token='YOUR TOKEN'

WEBHOOK_HOST = 'YOUR DOMAIN'
WEBHOOK_URL_PATH = 'bot'
WEBHOOK_PORT = os.environ.get('PORT',5000)
WEBHOOK_LISTEN = '0.0.0.0'


WEBHOOK_URL_BASE = "https://%s/%s"% (WEBHOOK_HOST,WEBHOOK_URL_PATH)


pattern = re.compile(r'^\w+', re.MULTILINE)
dirs=["az-ru","be-bg","be-cs","be-de","be-en","be-es","be-fr","be-it","be-pl","be-ro","be-ru","be-sr","be-tr","bg-be","bg-ru","bg-uk","ca-en","ca-ru","cs-be","cs-en","cs-ru","cs-uk","da-en","da-ru","de-be","de-en","de-es","de-fr","de-it","de-ru","de-tr","de-uk","el-en","el-ru","en-be","en-ca","en-cs","en-da","en-de","en-el","en-es","en-et","en-fi","en-fr","en-hu","en-it","en-lt","en-lv","en-mk","en-nl","en-no","en-pt","en-ru","en-sk","en-sl","en-sq","en-sv","en-tr","en-uk","es-be","es-de","es-en","es-ru","es-uk","et-en","et-ru","fi-en","fi-ru","fr-be","fr-de","fr-en","fr-ru","fr-uk","hr-ru","hu-en","hu-ru","hy-ru","it-be","it-de","it-en","it-ru","it-uk","lt-en","lt-ru","lv-en","lv-ru","mk-en","mk-ru","nl-en","nl-ru","no-en","no-ru","pl-be","pl-ru","pl-uk","pt-en","pt-ru","ro-be","ro-ru","ro-uk","ru-az","ru-be","ru-bg","ru-ca","ru-cs","ru-da","ru-de","ru-el","ru-en","ru-es","ru-et","ru-fi","ru-fr","ru-hr","ru-hu","ru-hy","ru-it","ru-lt","ru-lv","ru-mk","ru-nl","ru-no","ru-pl","ru-pt","ru-ro","ru-sk","ru-sl","ru-sq","ru-sr","ru-sv","ru-tr","ru-uk","sk-en","sk-ru","sl-en","sl-ru","sq-en","sq-ru","sr-be","sr-ru","sr-uk","sv-en","sv-ru","tr-be","tr-de","tr-en","tr-ru","tr-uk","uk-bg","uk-cs","uk-de","uk-en","uk-es","uk-fr","uk-it","uk-pl","uk-ro","uk-ru","uk-sr","uk-tr"]

bot = telebot.TeleBot(token)
server=Flask(__name__)

GETLANGS_BASE_URL = 'https://translate.yandex.net/api/v1.5/tr.json/getLangs?'
TRANSLATE_BASE_URL='https://translate.yandex.net/api/v1.5/tr.json/translate?'
DETECTLANG_BASE_URL='https://translate.yandex.net/api/v1.5/tr.json/detect?'
key = 'YOUR KEY'
ui='en'

class Dir:
    transdir="en-ru"
    first=True
    chatid=0
    fsup=False
d=Dir()

@bot.message_handler(func=lambda message: True,commands=['start'])
def start_handler(msg):
    howtoinline(msg)
    d.first=True

@bot.message_handler(commands=['help'])
def help_handler(msg):
    bot.send_message(msg.chat.id,'Available translation direction:\n')
    s=''
    i=0
    while i<len(dirs):
        s+=dirs[i]+', '
        i+=1
    bot.send_message(msg.chat.id, s[:len(s)-2])
dirr={}
@bot.message_handler(func=lambda message: True,commands=['setting'])
def setting_handler(msg):
    exit=inarr(msg.chat.id, None)
    if exit==None:
        exit='not set'
    
    try:
        bot.send_message(msg.chat.id, 'Your translation direction: ' + exit) 
    except Exception as e:
        logging.warning(str(e))
    #bot.send_message(msg.chat.id, 'Your translation direction: ' + exit)    

def howtoinline(msg):
    d.first=False
    keyboard = types.InlineKeyboardMarkup()
    switch_button = types.InlineKeyboardButton(text="Ok", switch_inline_query="~en-ru")
    keyboard.add(switch_button)
    bot.send_message(msg.chat.id, text="Look how the bot works", reply_markup=keyboard)
    bot.send_message(msg.chat.id, 'To change translation direction, write in inline query character "~" and then translation direction\n\nExample:\n@interpreter_bot ~en-ru text to translate')
    #finish(msg)
	
dir='en-ru'

@bot.inline_handler(lambda query: type(query.query)==str)
def query_text(query):
    try:
        matches = re.match(pattern, query.query)
    except AttributeError as e:
        logging.error(str(e))
    try: 
        fsup=False
        if (query.query[0]=='~'): 
            
            change=re.findall("~[a-z][a-z]-[a-z][a-z]", query.query)
            if (len(change[0])==6):
                id=query.from_user.id
                global dir
                dir=change[0][1:]
                di={id:dir}
                q=query.query[6:]
                exit=inarr(id,di)
            
            response=textInputRequest(fsup,exit,q, id)
            msg=InputHandler(response)
            r=types.InlineQueryResultArticle('1',q,types.InputTextMessageContent(msg[0]), description=msg[0],thumb_url='https://upload.wikimedia.org/wikipedia/commons/7/7b/Translate.com_Avatar_Icon.png')
            bot.answer_inline_query(query.id, [r], cache_time=60)
        else:  
            	
            id=query.from_user.id
            exit=inarr(id, None)	
            q=query.query
            id=query.from_user.id
            response=textInputRequest(fsup, exit, q, id)
            msg=InputHandler(response)
            r=types.InlineQueryResultArticle('1',q,types.InputTextMessageContent(msg[0]), description=msg[0],thumb_url='https://upload.wikimedia.org/wikipedia/commons/7/7b/Translate.com_Avatar_Icon.png')
            bot.answer_inline_query(query.id, [r], cache_time=60)
        
    except Exception as e:
        logging.warning(str(e))

def inarr(id,di):
    if (di==None):
        return(dirr.get(id))
    dirr.update(di)
    return(dirr.get(id))
	
		
	
def textInputRequest(fsup,dir, text, id):
    if not text:
        logging.warning('Error: - responseController.textInputRequest: No text input')
    try:
        if not fsup:
            check(dir, id)
        urlEncodePairs = { 'key': key, 'text': text, 'lang': dir } 
        encodedURL = requests.get(TRANSLATE_BASE_URL, params=urlEncodePairs)
        return encodedURL
    except Exception as e:
        logging.warning('Error: - responseController.textInputRequest: ' + str(e))

def check(dir, id):
    f=False
    i=0
    while i<len(dirs):
        if dir==dirs[i]:
            f=True
            break
        i+=1
    if not f:
        bot.send_message(id, 'Translation direction %s is not supported' % dir)
		
def InputHandler(response):
    if response.status_code == 200:
        text=response.json().get('text')
        return text
    else:
        errorCode = response.json().get('message')
        sendTextMessage(str(response.status_code) + ' - ' + errorCode)
	
	
@server.route("/bot", methods=['POST'])
def getMessage():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

# Установка webhook
@server.route("/")
def webhook():
    bot.remove_webhook()
    return "%s" %bot.set_webhook(url=WEBHOOK_URL_BASE), 200

@server.route("/remove")
def remove_hook():
    bot.remove_webhook()
    return "Webhook has been removed"

server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
webhook()
