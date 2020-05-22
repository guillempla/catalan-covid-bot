import difflib
from plots import Plots
from tests import Tests
from deaths import Deaths
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


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
    description = 'None'
    if type == -1:
        fail_text = "Escriu el nom d'un municipi o d'una comarca vàlid si us plau. Clica a /comarques o /municipis."
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)
    else:
        if type == 0:
            deaths = Deaths(region)
            tests = Tests(region, 'comarcadescripcio')
            printCountyInformation(update, context, tests, deaths)
        elif type == 1:
            tests = Tests(region, 'municipidescripcio')
            printCountyInformation(update, context, tests, "None")


# send a message to the user with the information of covid
def printCountyInformation(update, context, tests, deaths):
    msg = tests.region + ":\n" +\
        "El nombre de casos positius és de " + str(tests.positive_cases) + "\n" +\
        "El nombre de casos sospitosos és de " + str(tests.probable_cases) + "\n"
    if deaths != "None":
        msg = msg + "El nombre de defuncions és de " + str(deaths.total_deaths) + "\n\n"
        if deaths.last_death != 'None':
            msg = msg + "L'última defunció és del dia " + deaths.last_death + "\n"

    if tests.last_positive != 'None':
        msg = msg + "L'últim positiu és del dia " + tests.last_positive + "\n"

    if tests.last_test != 'None':
        msg = msg + "L'última dada és del dia " + tests.last_test
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=msg, parse_mode=ParseMode.MARKDOWN)


# print a error message when the database is empty
def printMaintenance(update, context):
    maintenance_text = "La base de dades de la Generalitat de Catalunya està en manteniment. També pots consultar el nombre de tests realitzats al següent link:\n" +\
        "http://aquas.gencat.cat/ca/actualitat/ultimes-dades-coronavirus/mapa-per-municipis/"
    context.bot.send_message(chat_id=update.message.chat_id, text=maintenance_text)


# executed when the /comarques command is called
def plot(update, context):
    region = update.message.text[8:]  # delete "/grafic "
    print(update.message.from_user.full_name)
    print('Grafic '+region)
    region, type = typeOfRegion(region)
    description = 'None'
    if type == -1:
        fail_text = "Escriu el nom d'un municipi o d'una comarca vàlid si us plau. Clica a /comarques o /municipis."
        context.bot.send_message(chat_id=update.message.chat_id, text=fail_text)
    else:
        description = 'comarcadescripcio'
        if type == 1:
            description = 'municipidescripcio'
        plot = Plots(region, description)
        path = 'plots_accumulated/' + region + '.png'
        context.bot.send_photo(chat_id=update.message.chat_id,
                               photo=open(str(path), 'rb'))

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

# when the bot receives a command its functionis executed
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('comarques', comarques))
updater.dispatcher.add_handler(CommandHandler('municipis', municipis))
updater.dispatcher.add_handler(CommandHandler('grafic', plot))

# handling callbacks functions to the commands
updater.dispatcher.add_handler(MessageHandler(Filters.text, query))

# starts the bot
updater.start_polling()
