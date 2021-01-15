import os
import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta


class Tests:

    def __init__(self, region, description):
        self.limit = 400000
        self.dataset_link = "analisi.transparenciacatalunya.cat"
        self.dataset_id = "jj6z-iyrp"
        self.region = region
        self.description = description
        self.total_tests = 0
        self.positive_cases = 0
        self.probable_cases = 0
        self.last_test = 'None'
        self.last_positive = 'None'
        self.calculateInformation()

    # update tests' dataset
    def updateDatabase(self):
        f = open("./text/last_update_tests.txt").read().strip()
        last_update = datetime.strptime(f, "%Y-%m-%dT%H:%M:%S")
        if datetime.now()-last_update > timedelta(hours=8):
            f = open("./text/last_update_tests.txt", "w")
            f.write((datetime.now()).strftime("%Y-%m-%dT%H:%M:%S"))
            f.close()
            client = Socrata(self.dataset_link, None)
            data = client.get(self.dataset_id, limit=self.limit)
            df = pd.DataFrame.from_dict(data)
            print("updated")
            if self.checkDataIntegrity(df):
                df.to_pickle("./text/tests_backup.pkl")
                return df
            else:
                df = pd.read_pickle("./text/tests_backup.pkl")
                print("Malament")
                return df
        else:
            df = pd.read_pickle("./text/tests_backup.pkl")
            return df

    def checkDataIntegrity(self, df):
        df_sort = df.loc[df['municipidescripcio'] == 'SORT']
        df_jussa = df.loc[df['comarcadescripcio'] == 'PALLARS JUSSA']
        if len(df_sort) < 25 or len(df_jussa) < 100:
            return False
        return True

    # converts date_string into a datetime object and returns the maximum date
    def updateMaxDate(self, date, date_string):
        date_string = date_string[:date_string.find('.')]
        if date == 'None':
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        else:
            aux_date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            if aux_date > date:
                date = aux_date
        return date

    # Returns true if df is a positive result, otherwise returns false
    def positive(self, df):
        column = 'resultatcoviddescripcio'
        return (df[column] == 'Positiu PCR') | (df[column] ==
                                                'Positiu per Test Ràpid') | (df[column] == 'Positiu per ELISA') | (df[column] == 'Epidemiològic')  | (df[column] == 'Positiu TAR')

    # Returns true if df is a positive result, otherwise returns false
    def negative(self, df):
        column = 'resultatcoviddescripcio'
        return df[column] == 'Sospitós'

    # calculates the number of cases for the region given
    def calculateInformation(self):
        df = self.updateDatabase()
        df_region = df.loc[df[self.description] == self.region]

        if self.region == "CATALUNYA":
            df_region = df

        df_positives = df_region.loc[self.positive]

        self.total_tests = df_region['numcasos'].astype(int).sum()
        self.positive_cases = df_positives['numcasos'].astype(int).sum()

        if self.total_tests > 0:
            self.last_test = df_region['data'].max()
            self.last_test = datetime.strptime(
                self.last_test[:self.last_test.find('.')], "%Y-%m-%dT%H:%M:%S")
            self.last_test = self.last_test.strftime("%d/%m/%Y")

        if self.positive_cases > 0:
            self.last_positive = df_positives['data'].max()
            self.last_positive = datetime.strptime(
                self.last_positive[:self.last_positive.find('.')], "%Y-%m-%dT%H:%M:%S")
            self.last_positive = self.last_positive.strftime("%d/%m/%Y")
