# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
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
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.set_defaults(place=False, debug=False)

    args = parser.parse_args()

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:

                if args.place:
                    print(scraper.get_account(url))
                else:
                    error = scraper.sort_by_date(url)
                    if error == 0:

                        # store reviews in CSV file
                        writer = csv_writer()

                        n = 0
                        while n < args.N:
                            reviews = scraper.get_reviews(n)

                            for r in reviews:
                                writer.writerow(list(r.values()))

                            n += len(reviews)
