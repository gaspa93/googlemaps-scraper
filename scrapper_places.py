from googlemaps import GoogleMapsScraper
import argparse
import csv
from termcolor import colored
import pandas as pd


if __name__ == '__main__':

    scraper = GoogleMapsScraper()

    #scraper.get_places(method='squares', keyword_list=['laser'])
    urls=scraper._gen_search_points_from_square(keyword_list=["romantic restaurant"])

    for u in urls:
        print(u)
