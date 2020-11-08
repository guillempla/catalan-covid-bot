import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta, MINYEAR
from pandas.plotting import register_matplotlib_converters
from matplotlib.dates import DayLocator, MonthLocator, YearLocator, DateFormatter, date2num

XLIMIT = 0
YLIMIT = 1500
DAYSAGO = 70

class Plots:

    def __init__(self, region, population, description):    
        # Register convertes
        register_matplotlib_converters()

        # Set the style
        plt.style.use(u'seaborn')

        # self.plot(self.date, self.positive_cases, self.deaths, 'plots/')
        # self.plot_accumulated(self.date, self.positive_accumulated,
        #           self.deaths_accumulated, 'plots_accumulated/')
        self.plot_daily(self.date, self.positive_cases,
                  self.deaths, self.positive_average, 'plots_daily/')
        if (self.description == 'comarcadescripcio'):
            self.plot_incidence(self.date, self.positive_incidence,
                      self.deaths_incidence, 'plots_incidence/')

        self.file_path = ''

    def reduce_data(self, data):
        return data = data[len(data)-DAYSAGO:]

    def bold(self, string):
        bold = ''
        array = string.split(' ')
        for a in array:
            bold = bold + ' ' + '$\\bf{' + a + '}$'
        return bold

    def plot_accumulated(self, X, Y, Z, A, path):
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
        Yl = np.ma.masked_inside(Y, 50, 5000)
        Ym = np.ma.masked_inside(Y, 0, 50)
        Yh = np.ma.masked_inside(Y, 0, 150)
        Ye = np.ma.masked_inside(Y, 0, 250)

        # Add data
        ax.bar(X, Yl, color = mcolors.CSS4_COLORS['green'], linewidth=1.8, label='Risc baix (IA14 inferior a 50)', align='center')
        ax.bar(X, Ym, color = mcolors.CSS4_COLORS['darkorange'], linewidth=1.8, label='Risc mitjà (IA entre 50 i 150)', align='center')
        ax.bar(X, Yh, color = mcolors.CSS4_COLORS['red'], linewidth=1.8, label='Risc alt (IA entre 150 i 250)', align='center')
        ax.bar(X, Ye, color = mcolors.CSS4_COLORS['darkred'], linewidth=1.8, label='Risc extrem (IA superior a 250)', align='center')

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

    def plot_daily(self, X, Y, Z, A, path):
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
        ax.plot(X, A, 'k-x', label='Mitjana mòbil de 7 dies')
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
