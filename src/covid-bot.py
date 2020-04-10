import os
import pandas as pd
from sodapy import Socrata
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def writeCountyProperly(county):
    original_counties = [line.strip() for line in open('./text/counties.txt')]
    return original_counties[COUNTIES.index(county)]


def updateDatabase():
    # load the tests dataset's client
    client = Socrata(dataset_link, socrata_token)
    data = client.get(dataset_id, limit=LIMIT)
    df = pd.DataFrame.from_dict(data)
    # dataset contains extra characters on those counties finished with 'à'
    df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
        "\xa0", "")
    df['comarcadescripcio'] = df['comarcadescripcio'].str.replace("à", "a")
    df['comarcadescripcio'] = df['comarcadescripcio'].str.replace("è", "e")
    df['comarcadescripcio'] = df['comarcadescripcio'].str.lower()
    return df


# calculates the number of cases for the county
def getNumberCases(county):
    df = updateDatabase()
    df_county = df.loc[df['comarcadescripcio'] == county]
    total_tests = 0
    positive_cases = 0
    negative_cases = 0
    for index, row in df_county.iterrows():
        total_tests += int(row['numcasos'])
        if row['resultatcoviddescripcio'] == 'Positiu':
            positive_cases += int(row['numcasos'])
        elif row['resultatcoviddescripcio'] == 'Negatiu':
            negative_cases += int(row['numcasos'])
    return (str(positive_cases), str(negative_cases), str(total_tests))


# send a message to the user with the information of covid
def printCountyInformation(update, context, county, positive, negative, total):
    msg = writeCountyProperly(county) + ":\n" +\
        "El nombre de casos positius és de " + positive + "\n" +\
        "El nombre de casos negatius és de " + negative + "\n" +\
        "El nombre total de tests que s'han realitzat és de " + total
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=msg, parse_mode=ParseMode.MARKDOWN)


# executed when the bot receives a message
def counties(update, context):
    county = update.message.text
    county = county.replace("à", "a").replace("è", "e").lower()
    if county in COUNTIES:
        positive, negative, total = getNumberCases(county)
        printCountyInformation(update, context, county, positive, negative, total)
    else:
        fail_text = "Escriu una comarca vàlida si us plau. Consulta a /help les comarques."
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)


# executed when the /help command is called
def help(update, context):
    help_text = open('./text/help.txt').read()
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=help_text, parse_mode=ParseMode.MARKDOWN)


# executed when the /start command is called
def start(update, context):
    info_text = "El bot s'ha inicializat correctament!!"
    context.bot.send_message(chat_id=update.message.chat_id, text=info_text)


# build the object to work with Telegram
TOKEN = open('./text/token.txt').read().strip()
updater = Updater(token=TOKEN, use_context=True)

# load Catalan counties list
COUNTIES = [line.strip().replace("à", "a").replace("è", "e").lower()
            for line in open('./text/counties.txt')]
# load the socrata token and the dataset_id
socrata_token = os.environ.get("SODAPY_APPTOKEN")
dataset_link = "analisi.transparenciacatalunya.cat"
dataset_id = "jj6z-iyrp"
LIMIT = 50000
# when the bot receives a command its functionis executed
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))

# handling callbacks functions to the commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, counties))

# starts the bot
updater.start_polling()
