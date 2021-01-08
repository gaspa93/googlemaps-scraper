#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import logging
import sys

DB_URL = 'mongodb://localhost:27017/'
DB_NAME = 'googlemaps'
COLLECTION_NAME = 'review'

class Monitor:

    def __init__(self, url_file, from_date, mongourl=DB_URL):

        # load urls file
        with open(url_file, 'r') as furl:
            self.urls = [u[:-1] for u in furl]

        # define MongoDB connection
        self.client = MongoClient(mongourl)

        # min date review to scrape
        self.min_date_review = datetime.strptime(from_date, '%Y-%m-%d')

        # logging
        self.logger = self.__get_logger()

    def scrape_gm_reviews(self):
        # set connection to DB
        collection = self.client[DB_NAME][COLLECTION_NAME]

        # init scraper and incremental add reviews
        # TO DO: pass logger as parameter to log into one single file?
        with GoogleMapsScraper() as scraper:
            for url in self.urls:
                try:
                    error = scraper.sort_by_date(url)
                    if error == 0:
                        stop = False
                        offset = 0
                        n_new_reviews = 0
                        while not stop:
                            rlist = scraper.get_reviews(offset)
                            for r in rlist:
                                # calculate review date and compare to input min_date_review
                                r['timestamp'] = self.__parse_relative_date(r['relative_date'])
                                stop = self.__stop(r, collection)
                                if not stop:
                                    collection.insert_one(r)
                                    n_new_reviews += 1
                                else:
                                    break
                            offset += len(rlist)

                        # log total number
                        self.logger.info('{} : {} new reviews'.format(url, n_new_reviews))
                    else:
                        self.logger.warning('Sorting reviews failed for {}'.format(url))

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                    self.logger.error('{}: {}, {}, {}'.format(url, exc_type, fname, exc_tb.tb_lineno))


    def __parse_relative_date(self, string_date):
        curr_date = datetime.now()
        split_date = string_date.split(' ')

        n = split_date[0]
        delta = split_date[1]

        if delta == 'year':
            return curr_date - timedelta(days=365)
        elif delta == 'years':
            return curr_date - timedelta(days=365 * int(n))
        elif delta == 'month':
            return curr_date - timedelta(days=30)
        elif delta == 'months':
            return curr_date - timedelta(days=30 * int(n))
        elif delta == 'week':
            return curr_date - timedelta(weeks=1)
        elif delta == 'weeks':
            return curr_date - timedelta(weeks=int(n))
        elif delta == 'day':
            return curr_date - timedelta(days=1)
        elif delta == 'days':
            return curr_date - timedelta(days=int(n))
        elif delta == 'hour':
            return curr_date - timedelta(hours=1)
        elif delta == 'hours':
            return curr_date - timedelta(hours=int(n))
        elif delta == 'minute':
            return curr_date - timedelta(minutes=1)
        elif delta == 'minutes':
            return curr_date - timedelta(minutes=int(n))
        elif delta == 'moments':
            return curr_date - timedelta(seconds=1)


    def __stop(self, r, collection):
        is_old_review = collection.find_one({'id_review': r['id_review']})
        if is_old_review is None and r['timestamp'] >= self.min_date_review:
            return False
        else:
            return True

    def __get_logger(self):
        # create logger
        logger = logging.getLogger('monitor')
        logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        fh = logging.FileHandler('monitor.log')
        fh.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # add formatter to ch
        fh.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(fh)

        return logger


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Monitor Google Maps places')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--from-date', type=str) # start date in format: YYYY-MM-DD

    args = parser.parse_args()

    monitor = Monitor(args.i, args.from_date)

    try:
        monitor.scrape_gm_reviews()
    except Exception as e:
        monitor.logger.error('Not handled error: {}'.format(e))
