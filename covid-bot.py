from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def counties(update, context):
    county = update.message.text
    if county in COUNTIES:
        context.bot.send_message(chat_id=update.message.chat_id, text=county)
    else:
        fail_text = "Aquesta comarca no existeix"
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)


def start(update, context):
    init_text = '''
El bot s'ha inicialitzat correctament!
Escriu el nom d'una *comarca* i obtindràs les seves dades.
'''
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=init_text, parse_mode=telegram.ParseMode.MARKDOWN)


# build the object to work with Telegram
TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)

# load Catalan counties list
COUNTIES = set(line.strip() for line in open('counties.txt'))

# when the bot receives the command /start the function start is executed
updater.dispatcher.add_handler(CommandHandler('start', start))

# handling callbacks functions to the commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, counties))

# starts the bot
updater.start_polling()
