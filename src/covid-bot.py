import os
import difflib
import pandas as pd
from sodapy import Socrata
from datetime import datetime
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# load the tests dataset's client
def updateDatabase():
    client = Socrata(dataset_link, socrata_token)
    data = client.get(dataset_id, limit=LIMIT)
    df = pd.DataFrame.from_dict(data)
    # dataset contains extra characters on those counties finished with 'à'
    try:
        df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
            "\xa0", "")
        df['municipidescripcio'] = df['municipidescripcio'].str.replace(
            "\xa0", "")
        df.to_pickle("./text/dataframe_backup.pkl")
        return df
    except KeyError:
        raise KeyError


# converts date_string into a datetime object and returns the maximum date
def updateMaxDate(max_date, date_string):
    date_string = date_string[:date_string.find('.')]
    if max_date == 'None':
        max_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    else:
        aux_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        if aux_date > max_date:
            max_date = aux_date
    return max_date


# calculates the number of cases for the region given
def getNumberCases(region, description):
    try:
        df = updateDatabase()
    except KeyError:
        raise KeyError
    df_region = df.loc[df[description] == region]
    total_tests = 0
    positive_cases = 0
    probable_cases = 0
    max_date = 'None'
    for index, row in df_region.iterrows():
        total_tests += int(row['numcasos'])
        max_date = updateMaxDate(max_date, row['data'])
        if row['resultatcoviddescripcio'] == 'Positiu':
            positive_cases += int(row['numcasos'])
        elif row['resultatcoviddescripcio'] == 'Sospitós':
            probable_cases += int(row['numcasos'])
    if max_date != 'None':
        max_date = max_date.strftime("%d/%m/%Y")
    return (str(positive_cases), str(probable_cases), str(total_tests), max_date)


# decides which type of region is the region given
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
    print(update.message.from_user.full_name)
    print(region)
    region, type = typeOfRegion(region)
    descripcio = 'None'
    if type == -1:
        fail_text = "Escriu el nom d'un municipi o d'una comarca vàlid si us plau. Clica a /comarques o /municipis."
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)
    else:
        if type == 0:
            descripcio = 'comarcadescripcio'
        elif type == 1:
            descripcio = 'municipidescripcio'
        try:
            positive, negative, total, date = getNumberCases(region, descripcio)
            printCountyInformation(update, context, region, positive, negative, total, date)
        except KeyError:
            printMaintenance(update, context)


# send a message to the user with the information of covid
def printCountyInformation(update, context, region, positive, probable, total, date):
    msg = region + ":\n" +\
        "El nombre de casos positius és de " + positive + "\n" +\
        "El nombre de casos sospitosos és de " + probable + "\n\n"
    if date != 'None':
        msg = msg + "L'última dada és del dia " + date
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=msg, parse_mode=ParseMode.MARKDOWN)


# print a error message when the database is empty
def printMaintenance(update, context):
    maintenance_text = "La base de dades de la Generalitat de Catalunya està en manteniment. També pots consultar el nombre de tests realitzats al següent link:\n" +\
        "http://aquas.gencat.cat/ca/actualitat/ultimes-dades-coronavirus/mapa-per-municipis/"
    context.bot.send_message(chat_id=update.message.chat_id, text=maintenance_text)


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
