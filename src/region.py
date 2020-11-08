import numpy as np
import pandas as pd
from datetime import datetime, timedelta, MINYEAR

INITIAL_DATE = datetime(2020, 3, 3)

class Region:

    def __init__(self, name, population, description):
        self.date = np.arange(INITIAL_DATE, datetime.today(), timedelta(days=1)).astype(datetime)

        self.name = region
        self.description = description
        self.population = population

        # Tests and Deaths
        self.positive_cases
        self.probable_cases
        self.total_deaths
        self.last_death
        self.last_positive
        self.last_test

        # Plots
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

        # # Load data in plots
        # self.df_tests = pd.read_pickle("./text/tests_backup.pkl")
        # self.df_deaths = pd.read_pickle("./text/deaths_backup.pkl")

    def stringToDatetime(self, date_string):
        date_string = date_string[:date_string.find('.')]
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

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

    def calculateAccumulated(self):
        self.positive_accumulated = np.cumsum(self.positive_cases)
        self.probable_accumulated = np.cumsum(self.probable_cases)
        self.deaths_accumulated = np.cumsum(self.deaths)

    def moving_average(self, a, n=7):
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n
