import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta, MINYEAR
from pandas.plotting import register_matplotlib_converters
from matplotlib.dates import DayLocator, MonthLocator, YearLocator, DateFormatter, date2num

XLIMIT = 0
YLIMIT = 1500
DAYSAGO = 70

class Plots:
    def __init__(self, region, population, description):
        self.region = region
        self.description = description
        self.population = population
        self.date = np.arange(datetime(2020, 3, 3), datetime.today(),
                              timedelta(days=1)).astype(datetime)

        self.pcr_cases = np.zeros(len(self.date))
        self.positive_cases = np.zeros(len(self.date))
        self.probable_cases = np.zeros(len(self.date))
        self.deaths = np.zeros(len(self.date))

        self.positive_incidence = np.zeros(len(self.date))
        self.probable_incidence = np.zeros(len(self.date))
        self.deaths_incidence = np.zeros(len(self.date))

        self.positive_accumulated = np.zeros(len(self.date))
        self.probable_accumulated = np.zeros(len(self.date))
        self.deaths_accumulated = np.zeros(len(self.date))

        self.df_tests = pd.read_pickle("./text/tests_backup.pkl")
        self.df_deaths = pd.read_pickle("./text/deaths_backup.pkl")

        # Calculate data
        self.calculateTests()
        if (self.description == 'comarcadescripcio'):
            self.calculateDeaths()
            self.calculateIncidence()
        self.calculateAccumulated()

        self.date = self.date[len(self.date)-DAYSAGO:]
        self.positive_cases = self.positive_cases[len(self.positive_cases)-DAYSAGO:]
        self.deaths = self.deaths[len(self.deaths)-DAYSAGO:]
        self.positive_accumulated = self.positive_accumulated[len(self.positive_accumulated)-DAYSAGO:]
        self.deaths_accumulated = self.deaths_accumulated[len(self.deaths_accumulated)-DAYSAGO:]
        self.positive_incidence = self.positive_incidence[len(self.positive_incidence)-DAYSAGO:]

        print(self.positive_cases)

        # Register convertes
        register_matplotlib_converters()

        # Set the style
        plt.style.use(u'seaborn')

        # self.plot(self.date, self.positive_cases, self.deaths, 'plots/')
        # self.plot_accumulated(self.date, self.positive_accumulated,
        #           self.deaths_accumulated, 'plots_accumulated/')
        self.plot_daily(self.date, self.positive_cases,
                  self.deaths, 'plots_daily/')
        if (self.description == 'comarcadescripcio'):
            self.plot_incidence(self.date, self.positive_incidence,
                      self.deaths_incidence, 'plots_incidence/')

        self.file_path = ''

    def bold(self, string):
        bold = ''
        array = string.split(' ')
        for a in array:
            bold = bold + ' ' + '$\\bf{' + a + '}$'
        return bold

    def positive(self, data):
        return data == 'Positiu PCR' or data == 'Positiu per Test Ràpid' or data == 'Positiu per ELISA' or data == 'Epidemiològic'

    def pcr(self, data):
        return data == 'Positiu PCR' or data == 'Positiu per Test Ràpid'

    def negative(self, data):
        return data == 'Sospitós'

    def stringToDatetime(self, date_string):
        date_string = date_string[:date_string.find('.')]
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

    def calculateTests(self):
        df_tests_region = self.df_tests.loc[self.df_tests[self.description] == self.region]

        if self.region == "Catalunya":
            df_tests_region = self.df_tests

        for index, row in df_tests_region.iterrows():
            date_time = self.stringToDatetime(row['data'])
            date_index, = np.where(self.date == date_time)
            if self.pcr(row['resultatcoviddescripcio']):
                self.pcr_cases[date_index] += int(row['numcasos'])
            if self.positive(row['resultatcoviddescripcio']):
                self.positive_cases[date_index] += int(row['numcasos'])
            elif self.negative(row['resultatcoviddescripcio']):
                self.probable_cases[date_index] += int(row['numcasos'])

    def calculateDeaths(self):
        region = self.region
        if self.region == "Aran":
            region = "Val d'Aran"

        df_deaths_region = self.df_deaths.loc[self.df_deaths[self.description] == region]

        if self.region == "Catalunya":
            df_deaths_region = self.df_deaths

        for index, row in df_deaths_region.iterrows():
            date_time = self.stringToDatetime(row['exitusdata'])
            date_index, = np.where(self.date == date_time)
            self.deaths[date_index] += int(row['numexitus'])

    def calculateIncidence(self):
        for i in range(len(self.positive_incidence)-1, 0, -1):
            self.positive_incidence[i] = np.sum(self.pcr_cases[max(0, i-13):i])
            self.deaths_incidence[i] = np.sum(self.deaths[max(0, i-13):i])

        self.positive_incidence = np.multiply(np.divide(self.positive_incidence, self.population), 100000)
        self.deaths_incidence = np.multiply(np.divide(self.deaths_incidence, self.population), 100000)

    def calculateAccumulated(self):
        self.positive_accumulated = np.cumsum(self.positive_cases)
        self.probable_accumulated = np.cumsum(self.probable_cases)
        self.deaths_accumulated = np.cumsum(self.deaths)

    def plot_accumulated(self, X, Y, Z, path):
        # Create plot
        fig, ax = plt.subplots()

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
        ax.set_xlim([X[0], X[-1]])

        # Set the y axis number of ticks
        ax.locator_params(nbins=15, axis='y')

        # Add data
        ax.plot_accumulated(X, Y, marker='', color='red', linewidth=1.8, label='Casos Positius')
        if (self.description == 'comarcadescripcio'):
            ax.plot_accumulated(X, Z, marker='', color='black', linewidth=1.8, label='Defuncions')

        # Turn region name into bold string
        bold = self.bold(self.region)

        # Labels
        ax.set_title(bold)
        ax.set_xlabel('Data')
        ax.set_ylabel('Casos')
        ax.legend(loc='upper left', framealpha=0.5)

        plt.figtext(0.03, 0, "Font: Dades Obertes de la Generalitat de Catalunya",
                    ha="left", fontsize=7)
        plt.figtext(0.72, 0, "Bot de Telegram: t.me/CatalunyaCOVID19bot",
                    ha="left", fontsize=7)

        # Use tight layout
        fig.tight_layout()
        # Save
        self.file_path = path + self.region + '.png'
        plt.savefig(self.file_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_incidence(self, X, Y, Z, path):
        # Create plot
        fig, ax = plt.subplots()

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
        ax.set_xlim([X[0], X[-1]])

        ax.set_ylim(XLIMIT, YLIMIT)

        # Set risk masks
        Yl = np.ma.masked_inside(Y, 101, 2000)
        Yh = np.ma.masked_inside(Y, 0, 100)

        # Add data
        ax.bar(X, Yl, color = 'green', linewidth=1.8, label='Incidència acumulada per sota o igual de 100', align='center')
        ax.bar(X, Yh, color = 'red', linewidth=1.8, label='Incidència acumulada per sobre de 100', align='center')

        # Turn region name into bold string
        bold = self.bold(self.region)

        # Labels
        ax.set_title(bold + ': Incidència acumulada en els últims 14 dies')
        ax.set_xlabel('Data')
        ax.set_ylabel('IA14')
        ax.legend(loc='upper left', framealpha=0.5)

        plt.figtext(0.03, 0, "Font: Dades Obertes de la Generalitat de Catalunya",
                    ha="left", fontsize=7)
        plt.figtext(0.72, 0, "Bot de Telegram: t.me/CatalunyaCOVID19bot",
                    ha="left", fontsize=7)

        # Use tight layout
        fig.tight_layout()
        # Save
        self.file_path = path + self.region + '.png'
        plt.savefig(self.file_path, dpi=150, bbox_inches='tight')
        plt.close()

    def plot_daily(self, X, Y, Z, path):
        # Create plot
        fig, ax = plt.subplots()

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
        ax.set_xlim([X[0], X[-1]])

        # Add data
        ax.bar(X, Y, color = 'red', linewidth=1.8, label='Casos Positius', align='center')
        ax.bar(X, Z, color = 'black', linewidth=1.8, label='Defuncions', align='center')

        # Turn region name into bold string
        bold = self.bold(self.region)

        # Labels
        ax.set_title(bold + ': Casos i defuncions diaries')
        ax.set_xlabel('Data')
        ax.set_ylabel('Positius')
        ax.legend(loc='upper left', framealpha=0.5)

        plt.figtext(0.03, 0, "Font: Dades Obertes de la Generalitat de Catalunya",
                    ha="left", fontsize=7)
        plt.figtext(0.72, 0, "Bot de Telegram: t.me/CatalunyaCOVID19bot",
                    ha="left", fontsize=7)

        # Use tight layout
        fig.tight_layout()
        # Save
        self.file_path = path + self.region + '.png'
        plt.savefig(self.file_path, dpi=150, bbox_inches='tight')
        plt.close()
