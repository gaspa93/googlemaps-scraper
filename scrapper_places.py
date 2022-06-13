from googlemaps import GoogleMapsScraper
import argparse
import csv
from termcolor import colored
import pandas as pd


if __name__ == '__main__':

    # input: starting coordinates list (each is "central point for the search")
    # input: number of places for each coordinate
    with GoogleMapsScraper(debug=True) as scraper:
        scraper.get_places(keyword_list=["romantic restaurant"])
