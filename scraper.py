# -*- coding: utf-8 -*-
from googlemaps import GoogleMaps
from datetime import datetime, timedelta
import argparse
import csv

HEADER = ['id_review', 'caption', 'timestamp', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']

def csv_writer(path='data/', outfile='gm_reviews.csv'):
    targetfile = open(path + outfile, mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(HEADER)

    return writer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')

    args = parser.parse_args()

    with GoogleMaps() as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                error = scraper.sort_by_date(url)
                if error == 0:
                    reviews = scraper.get_reviews(0)

                    # store reviews in CSV file
                    writer = csv_writer()
                    for r in reviews:
                        writer.writerow(list(item.values()))
