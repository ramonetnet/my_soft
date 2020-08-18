#!/usr/bin/env python

# bot service

# versions

# v 1.a - 20200811 - start
# v 1.b - fix print() for python 3
# v 1.c - install module
# v 1.d - llegir temperatura
# v 1.e - no reiniciar
# v 1.f - send date()
# v 1.g - send external IP
# v 1.h - send hostname
# v 1.h - Exception at bot.polling
# v 1.i - define logger
# v 1.j - timeout 123
# v 1.k - log only ERROR
# v 1.l - log INFO
# v 1.m - log user info
# v 1.n - log 2nd print()
# v 1.o - get_me()
# v 1.p - my_user
# v 1.q - trace popen() result length and return error msg if too large

# This is a detailed example using almost every command of the API

# Pending
#   list known users
#   who sends "start" to new user
#   pescar error "too long" (/exec cat /etc/motd) - f.read()

# after modifyinf this code, do
#   sudo systemctl stop   my_bot
#   sudo systemctl start  my_bot
#   sudo systemctl status my_bot

# install
#   sudo pip3 install pyTelegramBotAPI

# few URLs we used
#   https://www.flopy.es/crea-un-bot-de-telegram-para-tu-raspberry-ordenale-cosas-y-habla-con-ella-a-distancia/
#   https://medium.com/@crvc1998/bot-de-telegram-para-interactuar-con-servidor-linux-centos-7-e0857fa824b7
#   https://github.com/eternnoir/pyTelegramBotAPI                                                               - telebot homepage at github
#   https://github.com/eternnoir/pyTelegramBotAPI/issues/474                                                    - bot.polling() Exception 
#   https://pypi.org/project/pyTelegramBotAPI/                                                                  - telebot at pip
#   https://pypi.org/project/pyTelegramBotAPI/#logging                                                          - logging details
#   https://docs.python.org/2/library/logging.html
#   https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python
#   https://github.com/python-telegram-bot/python-telegram-bot/wiki/Handling-network-errors
#   https://stackoverflow.com/questions/4271740/how-can-i-use-python-to-get-the-system-hostname

# few modules to import

import datetime                       # timestamp
from   gpiozero import CPUTemperature
import logging
import os
from   requests import get
import telebot
from   telebot import types
import time

# Telegram bot token :

TOKEN = '1136067683:AAGcHbGWS3ek1UdKvyRWC7Xtuv1DuyvT6A4'
 
# Logger
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)     # DEBUG, ERROR

knownUsers = [ ]                          # chat id
# Sebas  [304588090] 
# Miquel [441014222] 
# ESP    [453540582]
# Irina  [819799527]

userStep = {}                             # so they won't reset every time the bot restarts

szVersio = "1.q"

commands = {                              # command description used in the "help" command
             'start':  'Get used to the bot',
             'ajuda':  'Da informacion sobre los comandos disponibles',
             'exec':   'Ejecuta un comando',
             'temp':   'Comprueba la temperatura de la Raspberry',
             'eip':    'Mostra la IP externa',
             'data':   'Mostra la data actual',
             'hn':     'Mostra el hostname',
             'ver':    'Mostra la versio del programa',
             'reboot': 'Reinicia el servidor'
}
 
hideBoard = types.ReplyKeyboardRemove()     # if sent as reply_markup, will hide the keyboard
 
# error handling if user isn't known yet
# (obsolete once known users are saved to file, because all users
# had to use the /start command and are therefore known to the bot)

def get_user_step(uid):

    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
#         print( "New user detected, who hasn't used \"/start\" yet" )
        szStart = "New user detected, who hasn't used \"/start\" yet" 
        logger.info( szStart )
        return 0
 
# only used for console output now
def listener(messages):                        # When new messages arrive TeleBot will call this function.

    for m in messages:

        if m.content_type == 'text':

            # print the sent message to the console
#            print( str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text )
            szUser = str(m.chat.first_name) 
            szUser += "/" + str( my_user )
            szUser += " [" + str(m.chat.id) + "]: " 
            szUser += m.text 
            logger.info( szUser )
 
# ************************************ lets go ************************************ 
 
bot = telebot.TeleBot(TOKEN)               # create a new Telegram Bot object

bot.set_update_listener(listener)          # register listener
 
my_bot = bot.get_me()                      # getMe : 
my_user = my_bot.first_name                #  

# getMe() output : {'id': 1136067683, 'is_bot': True, 'first_name': 'mars_ubuntu', 'username': 'mars_super_bot', 'last_name': None,
#                   'language_code': None, 'can_join_groups': True, 'can_read_all_group_messages': False, 'supports_inline_queries': False} 

### =======================================================================================================

@bot.message_handler(commands=['start'])    # handle the "/start" command
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:
        knownUsers.append(cid) 
        userStep[cid] = 0
#        command_help(m) # show the new user the help page
 
## -------------------------------------------------------------

@bot.message_handler(commands=['ajuda'])    # help page
def command_help(m):
    cid = m.chat.id
    help_text = "Estos son los comandos disponibles: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)
 
## -------------------------------------------------------------

@bot.message_handler(commands=['reboot'])   # reboot command
def command_reboot(m):
    cid = m.chat.id
    szInit = "Segur que vols reiniciar el servidor, " + m.chat.first_name + " ?"
    bot.send_message( cid, szInit )
#    bot.send_message(cid, "Voy a reiniciar el servidor...")

    bot.send_chat_action(cid, 'typing')
    time.sleep(3)

    bot.send_message(cid, ".")
#     os.system("sudo shutdown -r now")
    bot.send_message( cid, "Versio {" + szVersio + "}" )
 
## -------------------------------------------------------------

@bot.message_handler(commands=['temp'])     # temperature command
def command_temp(m):
    cid = m.chat.id
    bot.send_message(cid, "Vamos a comprobar si has puesto caliente a tu equipo...")

    bot.send_chat_action(cid, 'typing')                                                 # show the bot "typing" (max. 5 secs)
    time.sleep(2)

    cpu = CPUTemperature()
    result = str( cpu.temperature )
    bot.send_message(cid, ">>>"+result)
 
## -------------------------------------------------------------

@bot.message_handler(commands=['exec'])     # ejecuta un comando
def command_exec(m):
    cid = m.chat.id
    bot.send_message(cid, "Ejecutando: "+m.text[len("/exec"):])

    bot.send_chat_action(cid, 'typing')                                                 # show the bot "typing" (max. 5 secs)
    time.sleep(2)

    f = os.popen(m.text[len("/exec"):])   # Open a pipe to or from command cmd. Return value is an open file object connected to the pipe, which can be read (default) or written
    result = f.read()                                                                   # verificar si hi ha hagut error

    szRead = str( result ) 
    lng = len( szRead )
    szRead = "*** f.read lng = "+str(lng)
    logger.warning( szRead )                                                            # log warning

    if ( lng <= 4086 ):
        bot.send_message(cid, "+++ Resultado: "+result)
    else:
        bot.send_message(cid, "--- Resultat massa llarg (>4.086)" )
 
## -------------------------------------------------------------

@bot.message_handler(commands=['data'])     # mostra la nostra data
def command_data(m):
    cid = m.chat.id
    now = datetime.datetime.now()
    szData = now.strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(cid, "our date is "+szData)

## -------------------------------------------------------------

@bot.message_handler(commands=['eip'])     # mostra la nostra IP externa
def command_eip(m):
    cid = m.chat.id
    eip = get( 'https://api.ipify.org' ).text
    bot.send_message( cid, "our external IP is "+eip)

## -------------------------------------------------------------

@bot.message_handler(commands=['hn'])      # mostra el nostre hostname
def command_hn(m):
    cid = m.chat.id
    bot.send_message( cid, "our hostname is "+os.uname()[1] )

## -------------------------------------------------------------

@bot.message_handler(commands=['ver'])     # mostra la versio del programa
def command_ver(m):
    cid = m.chat.id
    bot.send_message( cid, "versio "+szVersio )

### =======================================================================================================

# filter on a specific message
@bot.message_handler(func=lambda message: message.text == "Hola")
def command_text_hi(m):
    bot.send_message(m.chat.id, "Muy buenas")

@bot.message_handler(func=lambda message: message.text == "Hijoputa")
def command_text_hi(m):
    bot.send_message(m.chat.id, "Bocachancla")

@bot.message_handler(func=lambda message: message.text == "Hijo de puta")
def command_text_hi(m):
    bot.send_message(m.chat.id, "Chupacables")

@bot.message_handler(func=lambda message: message.text == "Capullo")
def command_text_hi(m):
    bot.send_message(m.chat.id, "Pagafantas")

    # default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    bot.send_message(m.chat.id, "No te entiendo, prueba con /ajuda")
 
### =======================================================================================================

try:

# Upon calling this function, TeleBot starts polling the Telegram servers for new messages.
# - none_stop: True/False (default False) - Don't stop polling when receiving an error from the Telegram servers
# - interval: True/False (default False) - The interval between polling requests
# - timeout: integer (default 20) - Timeout in seconds for long polling.

    bot.polling( none_stop=True, interval=0, timeout=123 )
#     bot.polling()

except Exception as e:

    logger.error(e)
    time.sleep(15)

