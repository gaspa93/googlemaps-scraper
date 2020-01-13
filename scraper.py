# -*- coding: utf-8 -*-
from googlemaps import GoogleMaps
from datetime import datetime, timedelta
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')

    args = parser.parse_args()

    with GoogleMaps(args.N) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                error = scraper.sort_by_date(url)
                if error == 0:
                    reviews = scraper.get_reviews(0)
                else:
                    print('Error')
