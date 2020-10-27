import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta, MINYEAR
from pandas.plotting import register_matplotlib_converters
from matplotlib.dates import DayLocator, MonthLocator, YearLocator, DateFormatter, date2num


class Plots:
    def __init__(self, region, population, description):
        self.region = region
        self.description = description
        self.population = population
        self.date = np.arange(datetime(2020, 3, 3), datetime.today(),
                              timedelta(days=1)).astype(datetime)
        self.date_second = np.arange(datetime(2020, 9, 1), datetime.today(),
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

        # self.plot(self.date, self.positive_cases, self.deaths, 'plots/')
        self.plot(self.date, self.positive_accumulated,
                  self.deaths_accumulated, 'plots_accumulated/')
        if (self.description == 'comarcadescripcio'):
            self.plot_incidence(self.date, self.positive_incidence,
                      self.deaths_incidence, 'plots_incidence/')

        self.file_path = ''

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

    def calculateAverage(self):
        self.positive_average = self.moving_average(self.positive_cases, n=4)
        self.probable_average = self.moving_average(self.probable_cases, n=4)
        self.deaths_average = self.moving_average(self.deaths, n=4)

    def calculateAccumulated(self):
        self.positive_accumulated = np.cumsum(self.positive_cases)
        self.probable_accumulated = np.cumsum(self.probable_cases)
        self.deaths_accumulated = np.cumsum(self.deaths)

    def plot(self, X, Y, Z, path):
        # Set the style
        plt.style.use(u'seaborn')

        # Create plot
        fig, ax = plt.subplots()

        # Register convertes
        register_matplotlib_converters()

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=3))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))

        # Set the y axis number of ticks
        ax.locator_params(nbins=15, axis='y')

        # Add data
        ax.plot(X, Y, marker='', color='red', linewidth=1.8, label='Casos Positius')
        if (self.description == 'comarcadescripcio'):
            ax.plot(X, Z, marker='', color='black', linewidth=1.8, label='Defuncions')

        # Print fases
        ax.axvline(x=datetime(2020, 3, 13), label="Inici Confinament",
                   color='grey', linewidth=1.75, linestyle=':')
        ax.axvline(x=datetime(2020, 6, 18), label="Fase de Represa",
                   color='grey', linewidth=1.25, linestyle='--')

        # Labels
        ax.set_title(self.region)
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
        # Set the style
        plt.style.use(u'seaborn')

        # Create plot
        fig, ax = plt.subplots()

        # Register convertes
        register_matplotlib_converters()

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=90, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=3))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))

        ax.set_ylim(0, 2000)

        # Set risk masks
        Yl = np.ma.masked_inside(Y, 101, 2000)
        Yh = np.ma.masked_inside(Y, 0, 100)

        # Add data
        ax.bar(X, Yl, color = 'green', linewidth=1.8, label='Incidència acumulada per sota o igual de 100')
        ax.bar(X, Yh, color = 'red', linewidth=1.8, label='Incidència acumulada per sobre de 100')


        # Print fases
        ax.axvline(x=datetime(2020, 3, 13), label="Inici Confinament",
                   color='grey', linewidth=1.75, linestyle=':')
        ax.axvline(x=datetime(2020, 6, 18), label="Fase de Represa",
                   color='grey', linewidth=1.25, linestyle='--')

        # Labels
        ax.set_title(self.region + ': Incidència acumulada en els últims 14 dies')
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
