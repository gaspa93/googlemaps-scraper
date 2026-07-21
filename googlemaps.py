# -*- coding: utf-8 -*-
import itertools
import logging
import re
import time
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions as Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

GM_WEBPAGE = 'https://www.google.com/maps/'
MAX_WAIT = 10
MAX_RETRY = 5
MAX_SCROLLS = 100

class GoogleMapsScraper:

    def __init__(self, debug=False):
        self.debug = debug
        self.driver = self.__get_driver()
        self.logger = self.__get_logger()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()

        return True
    
    def __get_logger(self):
        """
        Initializes and returns a logger instance for the GoogleMapsScraper class.
    
        This logger is configured to output log messages to the console using a stream handler.
        The log level is set to DEBUG if `self.debug` is True, otherwise it uses INFO level.
        It helps in monitoring the application's behavior, especially during development or debugging.
        """
        logger = logging.getLogger("GoogleMapsScraper")
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(ch)

        return logger
    
    def open_reviews(self, url):
        """
        Clicks the review button on a Google Maps page to open the reviews section.
        """
        
        self.driver.get(url)
        self.__click_on_cookie_agreement()

        try:
            el = self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Reviews for")]')
            # print("Element found:", el)
            el.click()
            time.sleep(2)
        except NoSuchElementException:
            # print("Element not found")
            self.logger.warn('Failed to find Reviews button')


    def sort_by(self, url, ind):
        """
        Clicks the review sort button on a Google Maps page 
        to select a sort option by index.
        """

        # self.driver.get(url)
        # self.__click_on_cookie_agreement()

        wait = WebDriverWait(self.driver, MAX_WAIT)

        # open dropdown menu
        clicked = False
        tries = 0
        while not clicked and tries < MAX_RETRY:
            menu_bt = None
            try:
                menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label=\'Most relevant\']')))
            except TimeoutException:
                try:
                    menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
                except TimeoutException:
                    self.logger.warn('Failed to find Most relevant or Sort Button')
            
            if menu_bt:
                try:
                    menu_bt.click()
                    clicked = True
                    time.sleep(3)
                except Exception as e:
                    self.logger.warn(f'Failed to click the button: {e}')
            tries += 1

        if not clicked:
            return -1

        #  element of the list specified according to ind
        recent_rating_bt = self.driver.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[ind]
        recent_rating_bt.click()

        # wait to load review (ajax call)
        time.sleep(5)

        return 0

    def get_places(self, keyword_list=None):

        df_places = pd.DataFrame()
        search_point_url_list = self._gen_search_points_from_square(keyword_list=keyword_list)

        for i, search_point_url in enumerate(search_point_url_list):
            print(search_point_url)

            if (i+1) % 10 == 0:
                print(f"{i}/{len(search_point_url_list)}")
                df_places = df_places[['search_point_url', 'href', 'name', 'rating', 'num_reviews', 'close_time', 'other']]
                df_places.to_csv('output/places_wax.csv', index=False)


            try:
                self.driver.get(search_point_url)
            except NoSuchElementException:
                self.driver.quit()
                self.driver = self.__get_driver()
                self.driver.get(search_point_url)

            # scroll to load all (20) places into the page
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR,
                "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div[aria-label*='Results for']")
            for i in range(10):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

            # Get places names and href
            time.sleep(2)
            response = BeautifulSoup(self.driver.page_source, 'html.parser')
            div_places = response.select('div[jsaction] > a[href]')

            for div_place in div_places:
                place_info = {
                    'search_point_url': search_point_url.replace('https://www.google.com/maps/search/', ''),
                    'href': div_place['href'],
                    'name': div_place['aria-label']
                }

                df_places = df_places.append(place_info, ignore_index=True)

            # TODO: implement click to handle > 20 places

        df_places = df_places[['search_point_url', 'href', 'name']]
        df_places.to_csv('output/places_wax.csv', index=False)



    def get_reviews(self, offset):
        print(f"offset: {offset}")
        # scroll to load reviews
        print("Scrolling to load reviews...")
        self.__scroll()

        # wait for other reviews to load (ajax)
        print("Waiting for reviews to load(ajax)...")
        time.sleep(4)

        # expand review text
        print("Expanding reviews...")
        self.__expand_reviews()

        # parse reviews
        response = BeautifulSoup(self.driver.page_source, 'html.parser')
        # TODO: Subject to changes
        rblock = response.find_all('div', class_='jftiEf fontBodyMedium')
        parsed_reviews = []
        for index, review in enumerate(rblock):
            print(f"Parsing review {index}...")
            # print(review)
            
            # Dont parse all reviews, just the ones after offset
            if index >= offset:
                print(f"{index} >= {offset}")
                r = self.__parse(review)
                parsed_reviews.append(r)

                # logging to std out
                # print(r)
        return parsed_reviews



    # need to use different url wrt reviews one to have all info
    def get_account(self, url):
        print("Getting account data from url:", url)
        self.driver.get(url)
        time.sleep(3)
        # try:
        #     el = self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Reviews for")]')
        #     print("Element found:", el)
        # except NoSuchElementException:
        #     print("Element not found")

        # print(self.driver.find_element(By.XPATH, '//button[contains(@aria-label, "Reviews for"])'))#.click()
        # WebDriverWait(self.driver, 10).until(
        #     EC.element_to_be_clickable(
        #         (By.XPATH, '//button[contains(@aria-label, "Reviews for")]'))).click()

        # recent_rating_bt = self.driver.find_elements(By.XPATH, '//div[@role=\'menuitemradio\']')[ind]

        self.__click_on_cookie_agreement()

        # ajax call also for this section
        time.sleep(2)

        resp = BeautifulSoup(self.driver.page_source, 'html.parser')

        place_data = self.__parse_place(resp, url)

        return place_data


    def __parse(self, review):
        item = {}

        try:
            # TODO: 
            id_review = review['data-review-id']
        except Exception as e:
            id_review = None
            self.logger.warn('Failed to find and parse id_review')

        try:
            # TODO: 
            username = review['aria-label']
        except Exception as e:
            self.logger.warn('Failed to find and parse username')
            username = None
        
        try:
            # TODO:
            review_text = self.__filter_string(review.find('span', class_='wiI7pd').text)
        except Exception as e:
            review_text = None
            self.logger.warn('Failed to find and parse review_text')

        #Optional
        # Retrieving additional information from reviews
        try:
            # TODO:
            html = review.find_all('div', class_='PBK6be')
            more_review_text = []
            for span in html:
                more_review_text.append(span.get_text(separator=' '))
        except Exception as e:
            more_review_text = None
            self.logger.warn('Failed to find and parse review_text')

        try:
            # TODO: 
            rating = review.find('span', class_='fzvQIb').get_text()
        except Exception as e:
            rating = None
            self.logger.warn('Failed to find and parse rating')
            

        try:
            # TODO: Subject to changes
            relative_date = review.find('span', class_='xRkPPb').text
        except Exception as e:
            relative_date = None
            self.logger.warn('Failed to find and parse relative_date')

        try:
            n_reviews = review.find('div', class_='RfnDt').text.split(' ')[3]
        except Exception as e:
            n_reviews = 0
            self.logger.warn('Failed to find and parse n_reviews')

        try:
            user_url = review.find('button', class_='WEBjve')['data-href']
        except Exception as e:
            user_url = None
            self.logger.warn('Failed to find and parse user_url')

        item['id_review'] = id_review
        item['caption'] = review_text
        item['more_caption'] = more_review_text

        # depends on language, which depends on geolocation defined by Google Maps
        # custom mapping to transform into date should be implemented
        item['relative_date'] = relative_date

        # store datetime of scraping and apply further processing to calculate
        # correct date as retrieval_date - time(relative_date)
        item['retrieval_date'] = datetime.now()
        item['rating'] = rating
        item['username'] = username
        item['n_review_user'] = n_reviews
        #item['n_photo_user'] = n_photos  ## not available anymore
        item['url_user'] = user_url

        return item


    def __parse_place(self, response, url):

        place = {}

        try:
            place['name'] = response.find('h1', class_='DUwDvf fontHeadlineLarge').text.strip()
        except Exception as e:
            place['name'] = None

        try:
            place['overall_rating'] = float(response.find('div', class_='F7nice ').find('span', class_='ceNzKf')['aria-label'].split(' ')[1])
        except Exception as e:
            place['overall_rating'] = None

        try:
            place['n_reviews'] = int(response.find('div', class_='F7nice ').text.split('(')[1].replace(',', '').replace(')', ''))
        except Exception as e:
            place['n_reviews'] = 0

        try:
            place['n_photos'] = int(response.find('div', class_='YkuOqf').text.replace('.', '').replace(',','').split(' ')[0])
        except Exception as e:
            place['n_photos'] = 0

        try:
            place['category'] = response.find('button', jsaction='pane.rating.category').text.strip()
        except Exception as e:
            place['category'] = None

        try:
            place['description'] = response.find('div', class_='PYvSYb').text.strip()
        except Exception as e:
            place['description'] = None

        b_list = response.find_all('div', class_='Io6YTe fontBodyMedium')
        try:
            place['address'] = b_list[0].text
        except Exception as e:
            place['address'] = None

        try:
            place['website'] = b_list[1].text
        except Exception as e:
            place['website'] = None

        try:
            place['phone_number'] = b_list[2].text
        except Exception as e:
            place['phone_number'] = None
    
        try:
            place['plus_code'] = b_list[3].text
        except Exception as e:
            place['plus_code'] = None

        try:
            place['opening_hours'] = response.find('div', class_='t39EBf GUrTXd')['aria-label'].replace('\u202f', ' ')
        except:
            place['opening_hours'] = None

        place['url'] = url

        lat, long, z = url.split('/')[6].split(',')
        place['lat'] = lat[1:]
        place['long'] = long

        return place


    def _gen_search_points_from_square(self, keyword_list=None):
        # TODO: Generate search points from corners of square

        keyword_list = [] if keyword_list is None else keyword_list

        square_points = pd.read_csv('input/square_points.csv')

        cities = square_points['city'].unique()

        search_urls = []

        for city in cities:

            df_aux = square_points[square_points['city'] == city]
            latitudes = df_aux['latitude'].unique()
            longitudes = df_aux['longitude'].unique()
            coordinates_list = list(itertools.product(latitudes, longitudes, keyword_list))

            search_urls += [f"https://www.google.com/maps/search/{coordinates[2]}/@{str(coordinates[1])},{str(coordinates[0])},{str(15)}z"
             for coordinates in coordinates_list]

        return search_urls


    # expand review description
    def __expand_reviews(self):
        print("Expanding reviews descriptions function is running...")
        buttons = self.driver.find_elements(By.CSS_SELECTOR,'button.w8nwRe.kyuRq')
        for button in buttons:
            # print(f"Expanding review description for button: {button}")
            self.driver.execute_script("arguments[0].click();", button)
        print("Expanding reviews descriptions finished.")


    def __scroll(self):
        # TODO:
        print("Scrolling function is running...")
        scrollable_div = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        last_height = 0
        for i in range(MAX_SCROLLS):
            try:
                print(f"Scroll iteration {i} — loaded more content.")
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(1)

                # check if the page can no longer be scrolled
                new_height = self.driver.execute_script('return arguments[0].scrollTop', scrollable_div)
                if new_height == last_height:
                    print(f"Stopping scroll at iteration {i} — no more content to load.")
                    break
                last_height = new_height
            except Exception as e:
                self.logger.error(f"Error during scrolling: {e}")
        print("Scrolling finished.")





    def __get_logger(self):
        # create logger
        logger = logging.getLogger('googlemaps-scraper')
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        fh = logging.FileHandler('gm-scraper.log')
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # add formatter to ch
        fh.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(fh)

        return logger


    def __get_driver(self, debug=False):
        options = Options()

        if not self.debug:
            # options.add_argument("--headless")
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-images')
            options.add_argument('--disable-blink-features=AutomationControlled')

        else:
            options.add_argument("--window-size=1366,768")

        options.add_argument("--disable-notifications")
        #options.add_argument("--lang=en-GB")
        options.add_argument("--accept-lang=en-GB")
        input_driver = webdriver.Chrome(service=Service(), options=options)

         # click on google agree button so we can continue (not needed anymore)
         # EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "I agree")]')))
        input_driver.get(GM_WEBPAGE)

        return input_driver

    # cookies agreement click
    def __click_on_cookie_agreement(self):
        try:
            agree = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Reject all")]')))
            agree.click()

            # back to the main page
            # self.driver.switch_to_default_content()

            return True
        except:
            return False

    # util function to clean special characters
    def __filter_string(self, str):
        strOut = str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        return strOut
