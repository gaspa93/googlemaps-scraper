#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv


class Monitor:

    def __init__(self, url_file, to_date, mongourl='mongodb://localhost:27017/'):

        # load urls file
        with open(url_file, 'r')as furl:
            self.urls = open(furl, 'r')

        # define MongoDB connection
        self.client = MongoClient(mongourl)

        # max date review to scrape
        to_date = min(datetime.strptime(to_date, '%Y-%m-%d'), datetime.today())
        self.max_date_review = to_date
        print(self.max_date_review)

        # logging
        self.logger = self.__get_logger()

    def scrape_gm_reviews(self):

        self.logger.info('GOOGLEMAPS')

        # set connection to DB
        collection = self.client['google-maps']['review']

        # init scraper and incremental add reviews
        with GoogleMapsScraper(logger=self.logger) as crawler:

            for url in self.urls:
                try:
                    error = scraper.sort_by_date(url)
                    if error == 0:
                        # iterate over reviews to get previous run
                        stop = False
                        offset = 0
                        n_new_reviews = 0
                        while not stop:
                            rlist = crawler.get_reviews(offset)
                            for r in rlist:
                                stop = self.__stop(r, collection)
                                if not stop:
                                    # insert to MongoDB
                                    collection.insert_one(r)
                                    n_new_reviews += 1
                                else:
                                    break
                            offset += len(rlist)

                        # log total number
                        self.logger.info('{} : {} new reviews'.format(url, n_new_reviews))
                    else:
                        self.logger.warning(
                            'Sorting reviews failed for {}'.format(url))
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                    self.logger.error('{}: {}, {}, {}'.format(url, exc_type, fname, exc_tb.tb_lineno))


    def __stop(self, r, collection):
        is_old_review = collection.find_one({'id_review': r['id_review']})
        if is_old_review is None and r['timestamp'] >= self.min_date_review:
            return False
        else:
            return True

    def __get_logger(self):
        # create logger
        logger = logging.getLogger('review-step')
        logger.setLevel(logging.DEBUG)
        log_path = 'log/review.log'
        if not os.path.isdir('log/'):
            os.mkdir('log/')
        # create console handler and set level to debug
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        # add formatter to ch
        fh.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(fh)
        return logger


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Monitor Google Maps places')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')

    # end date in format: YYYY-MM-DD
    parser.add_argument('--to_date', type=str, default=datetime.today())

    monitor = Monitor(args.i, args.to_date)

    try:
        monitor.scrape_gm_reviews()
    except Exception as e:
        monitor.logger.error('Not handled error: {}'.format(e))
