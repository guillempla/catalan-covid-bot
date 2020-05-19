import os
import pandas as pd
from sodapy import Socrata
from datetime import datetime, timedelta


class Tests:

    def __init__(self, region, description):
        self.limit = 50000
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
        if datetime.now()-last_update > timedelta(hours=1):
            f = open("./text/last_update_tests.txt", "w")
            f.write((datetime.now()).strftime("%Y-%m-%dT%H:%M:%S"))
            f.close()
            print("updated")
            client = Socrata(self.dataset_link, None)
            data = client.get(self.dataset_id, limit=self.limit)
            df = pd.DataFrame.from_dict(data)
            # dataset contains extra characters on those counties finished with 'à'
            try:
                df['comarcadescripcio'] = df['comarcadescripcio'].str.replace(
                    "\xa0", "")
                df['municipidescripcio'] = df['municipidescripcio'].str.replace(
                    "\xa0", "")
                df.to_pickle("./text/tests_backup.pkl")
                return df
            except KeyError:
                df = pd.read_pickle("./text/tests_backup.pkl")
                print("Malament")
                return df
        else:
            df = pd.read_pickle("./text/tests_backup.pkl")
            return df

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

    # calculates the number of cases for the region given
    def calculateInformation(self):
        df = self.updateDatabase()
        df_region = df.loc[df[self.description] == self.region]

        for index, row in df_region.iterrows():
            self.total_tests += int(row['numcasos'])
            self.last_test = self.updateMaxDate(self.last_test, row['data'])
            if row['resultatcoviddescripcio'] == 'Positiu PCR' or row['resultatcoviddescripcio'] == 'Positiu per Test Ràpid':
                self.last_positive = self.updateMaxDate(self.last_positive, row['data'])
                self.positive_cases += int(row['numcasos'])
            elif row['resultatcoviddescripcio'] == 'Sospitós':
                self.probable_cases += int(row['numcasos'])

        if self.last_test != 'None':
            self.last_test = self.last_test.strftime("%d/%m/%Y")

        if self.last_positive != 'None':
            self.last_positive = self.last_positive.strftime("%d/%m/%Y")
