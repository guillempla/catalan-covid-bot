import os
import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta


class Tests:

    def __init__(self):
        self.limit = 400000
        self.dataset_link = "analisi.transparenciacatalunya.cat"
        self.dataset_id = "jj6z-iyrp"

        self.df = self.updateDatabase()

    # update tests' dataset
    def updateDatabase(self):
        f = open("./text/last_update_tests.txt").read().strip()
        last_update = datetime.strptime(f, "%Y-%m-%dT%H:%M:%S")
        if datetime.now()-last_update > timedelta(hours=6):
            f = open("./text/last_update_tests.txt", "w")
            f.write((datetime.now()).strftime("%Y-%m-%dT%H:%M:%S"))
            f.close()
            print("updated")
            client = Socrata(self.dataset_link, None)
            data = client.get(self.dataset_id, limit=self.limit)
            df = pd.DataFrame.from_dict(data)
            if self.checkDataIntegrity(df):
                df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
                    "\xa0", "")
                df['municipidescripcio'] = df['municipidescripcio'].str.replace(
                    "\xa0", "")
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
        try:
            df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
                "\xa0", "")
            df['municipidescripcio'] = df['municipidescripcio'].str.replace(
                "\xa0", "")
        except KeyError:
            return False
        df_sort = df.loc[df['municipidescripcio'] == 'Sort']
        df_jussa = df.loc[df['comarcadescripcio'] == 'Pallars Jussà']
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

    # Returns true if data is a positive result, otherwise returns false
    def positive(self, data):
        return data == 'Positiu PCR' or data == 'Positiu per Test Ràpid' or data == 'Positiu per ELISA' or data == 'Epidemiològic'

    # Returns true if data is a pcr or a fast test positive
    def pcr(self, data):
        return data == 'Positiu PCR' or data == 'Positiu per Test Ràpid'

    # Returns true if df is a positive result, otherwise returns false
    def negative(self, data):
        return data == 'Sospitós'

    # calculates the number of cases for the region given
    def calculateBasicInformation(self, region, description):
        df_region = self.df.loc[self.df[description] == region]

        if region == "Catalunya":
            df_region = df

        df_positives = df_region.loc[self.positive]
        df_probable = df_region.loc[self.negative]

        self.total_tests = df_region['numcasos'].astype(int).sum()
        self.positive_cases = df_positives['numcasos'].astype(int).sum()
        self.probable_cases = df_probable['numcasos'].astype(int).sum()

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


    def calculateTests(self, region, description):
        df_region = self.df.loc[self.df[description] == region]

        if region == "Catalunya":
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
