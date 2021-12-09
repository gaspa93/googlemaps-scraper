from googlemaps import GoogleMapsScraper
import argparse
import csv
from termcolor import colored
import pandas as pd


if __name__ == '__main__':

    # df_coodinates = pd.read_csv('input/coordinates.csv')

    # df_coodinates = pd.read_csv('input/urls_places.csv')

    scraper = GoogleMapsScraper(debug=True)

    scraper.get_places(method='squares', keyword_list=['laser'])
