import os
import difflib
import pandas as pd
from sodapy import Socrata
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# load the tests dataset's client
def updateDatabase():
    client = Socrata(dataset_link, socrata_token)
    data = client.get(dataset_id, limit=LIMIT)
    df = pd.DataFrame.from_dict(data)
    # dataset contains extra characters on those counties finished with 'à'
    df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
        "\xa0", "")
    df['municipidescripcio'] = df['municipidescripcio'].str.replace(
        "\xa0", "")
    return df


# calculates the number of cases for the county
def getNumberCases(region, descripcio):
    df = updateDatabase()
    df_region = df.loc[df[descripcio] == region]
    total_tests = 0
    positive_cases = 0
    negative_cases = 0
    for index, row in df_region.iterrows():
        total_tests += int(row['numcasos'])
        if row['resultatcoviddescripcio'] == 'Positiu':
            positive_cases += int(row['numcasos'])
        elif row['resultatcoviddescripcio'] == 'Negatiu':
            negative_cases += int(row['numcasos'])
    return (str(positive_cases), str(negative_cases), str(total_tests))


# send a message to the user with the information of covid
def printCountyInformation(update, context, region, positive, negative, total):
    msg = region + ":\n" +\
        "El nombre de casos positius és de " + positive + "\n" +\
        "El nombre de casos negatius és de " + negative + "\n" +\
        "El nombre total de tests que s'han realitzat és de " + total
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=msg, parse_mode=ParseMode.MARKDOWN)


def typeOfRegion(region):
    closest_match = difflib.get_close_matches(region, REGIONS, cutoff=0.7)
    if len(closest_match) != 0:
        if closest_match[0] in COUNTIES:
            return (closest_match[0], 0)
        if closest_match[0] in MUNICIPALITIES:
            return (closest_match[0], 1)
    return ("None", -1)


# executed when the bot receives a message
def query(update, context):
    region = update.message.text
    print(region)
    region, type = typeOfRegion(region)
    if (type == 0):
        positive, negative, total = getNumberCases(region, 'comarcadescripcio')
        printCountyInformation(update, context, region, positive, negative, total)
    elif (type == 1):
        positive, negative, total = getNumberCases(region, 'municipidescripcio')
        printCountyInformation(update, context, region, positive, negative, total)
    else:
        fail_text = "Escriu el nom d'un municipi o d'una comarca vàlid si us plau. Clica a /comarques o /municipis."
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)


# executed when the /comarques command is called
def comarques(update, context):
    counties_text = open('./text/comarques.txt').read()
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=counties_text, parse_mode=ParseMode.MARKDOWN)


# executed when the municipis command is called
def municipis(update, context):
    municipalities_text = "Per a veure el llistat de municipis clica al següent enllaç:\n" +\
        "https://github.com/guillempla/catalan-covid-tests-bot/blob/master/text/municipalities_complete.txt"
    context.bot.send_message(chat_id=update.message.chat_id, text=municipalities_text)


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
COUNTIES = [line.strip() for line in open('./text/counties.txt')]
MUNICIPALITIES = [line.strip() for line in open('./text/municipalities_complete.txt')]
REGIONS = [line.strip() for line in open('./text/regions.txt')]

# load the socrata token and the dataset_id
socrata_token = os.environ.get("SODAPY_APPTOKEN")
dataset_link = "analisi.transparenciacatalunya.cat"
dataset_id = "jj6z-iyrp"
LIMIT = 50000

# when the bot receives a command its functionis executed
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('comarques', comarques))
updater.dispatcher.add_handler(CommandHandler('municipis', municipis))

# handling callbacks functions to the commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, query))

# starts the bot
updater.start_polling()
