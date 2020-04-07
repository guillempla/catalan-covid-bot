import pandas as pd
from sodapy import Socrata
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def counties(update, context):
    county = update.message.text
    if county in COUNTIES:
        # cases   = client.get("jj6z-iyrp", )
        msg = "El nombre de casos a " + county + "és de "
        context.bot.send_message(chat_id=update.message.chat_id, text=msg)
    else:
        fail_text = "Escriu una comarca vàlida si us plau"
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)


def start(update, context):
    info_text = "El bot s'ha inicializat correctament!!"
    context.bot.send_message(chat_id=update.message.chat_id, text=info_text)


# build the object to work with Telegram
TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)

# load Catalan counties list
COUNTIES = set(line.strip() for line in open('counties.txt'))

# load the tests dataset's client
client = Socrata("analisi.transparenciacatalunya.cat", None)

# when the bot receives the command /start the function start is executed
updater.dispatcher.add_handler(CommandHandler('start', start))

# handling callbacks functions to the commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, counties))

# starts the bot
updater.start_polling()
