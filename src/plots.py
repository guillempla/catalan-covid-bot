import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta, MINYEAR
from matplotlib.dates import DayLocator, DateFormatter, date2num


class Plots:
    def __init__(self, region, description):
        self.region = region
        self.description = description
        self.date = np.arange(datetime(2020, 3, 3), datetime.today(),
                              timedelta(days=1)).astype(datetime)

        self.positive_cases = np.zeros(len(self.date))
        self.probable_cases = np.zeros(len(self.date))
        self.deaths = np.zeros(len(self.date))

        # self.positive_average = np.zeros(len(self.date))
        # self.probable_average = np.zeros(len(self.date))
        # self.deaths_average = np.zeros(len(self.date))

        self.positive_accumulated = np.zeros(len(self.date))
        self.probable_accumulated = np.zeros(len(self.date))
        self.deaths_accumulated = np.zeros(len(self.date))

        self.df_tests = pd.read_pickle("./text/tests_backup.pkl")
        self.df_deaths = pd.read_pickle("./text/deaths_backup.pkl")

        # Calculate data
        self.calculateTests()
        if(self.description == 'comarcadescripcio'):
            self.calculateDeaths()
        # self.calculateAverage()
        self.calculateAccumulated()

        #self.plot(self.date[3:], self.positive_average, self.deaths_average, 'plots_average/')
        #self.plot(self.date, self.positive_cases, self.deaths, 'plots/')
        self.plot(self.date, self.positive_accumulated,
                  self.deaths_accumulated, 'plots_accumulated/')

        self.file_path = ''

    def getPath(self):
        return self.file_path

    def moving_average(self, a, n=3):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def stringToDatetime(self, date_string):
        date_string = date_string[:date_string.find('.')]
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

    def calculateTests(self):
        df_tests_region = self.df_tests.loc[self.df_tests[self.description] == self.region]

        if self.region == "Catalunya":
            df_tests_region = df

        for index, row in df_tests_region.iterrows():
            date_time = self.stringToDatetime(row['data'])
            date_index, = np.where(self.date == date_time)
            if row['resultatcoviddescripcio'] == 'Positiu PCR' or row['resultatcoviddescripcio'] == 'Positiu per Test Ràpid':
                self.positive_cases[date_index] += int(row['numcasos'])
            elif row['resultatcoviddescripcio'] == 'Sospitós':
                self.probable_cases[date_index] += int(row['numcasos'])

    def calculateDeaths(self):
        region = self.region
        if self.region == "Aran":
            region = "Val d'Aran"

        df_deaths_region = self.df_deaths.loc[self.df_deaths[self.description] == region]

        if self.region == "Catalunya":
            df_deaths_region = df

        for index, row in df_deaths_region.iterrows():
            date_time = self.stringToDatetime(row['exitusdata'])
            date_index, = np.where(self.date == date_time)
            self.deaths[date_index] += int(row['numexitus'])

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

        # Rotate datetimes
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        ax.xaxis.set_major_locator(DayLocator(interval=5))
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))

        # X-axis
        # ax.xaxis.set_major_locator(DayLocator())
        # ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))

        # Add data
        ax.plot(X, Y, marker='', color='red', linewidth=1.8, label='Casos Positius')
        if (self.description == 'comarcadescripcio'):
            ax.plot(X, Z, marker='', color='black', linewidth=1.8, label='Defuncions')

        # # Set fases date
        # fases = {
        #     "Inici Confinament": datetime(2020, 3, 13),
        #     "Fase 1": datetime(2020, 5, 11)
        # }
        #
        # # Print fases
        # for f in fases:
        #     plt.axvline(x=fases[f], label=f, color='grey', linewidth=1)

        # Labels
        ax.set_title(self.region)
        ax.set_xlabel('Data')
        ax.set_ylabel('Casos')
        ax.legend(loc='best', framealpha=0.5)

        # Use tight layout
        fig.tight_layout()
        # Save
        self.file_path = path + self.region + '.png'
        plt.savefig(self.file_path, dpi=150, bbox_inches='tight')
        plt.close()
