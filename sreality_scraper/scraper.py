import datetime
import logging
import re
import time
from pathlib import Path

import numpy as np

import unicodedata

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from database import SrealityDatabase
from srality_orm import AdvertisingModel

logger = logging.getLogger('scraper.py')


class RealityScraper:
    def __init__(self, db: SrealityDatabase, reality_type: str = 'apartments', deal_type: str = 'for-sale',
                 max_advertising: int = 500, error_buffer: int = 5):
        self.db = db
        self.page = 'page'
        self.language = '/en'
        self.search = 'search'
        self.base_url = Path(f'https://www.sreality.cz{self.language}/{self.search}')
        self.reality_type = reality_type
        self.deal_type = deal_type
        self.error_buffer = error_buffer
        self.max_advertising = max_advertising
        self.scrape_url = self.base_url / deal_type / reality_type
        self.reality_type = reality_type
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.browser = None

    def __call__(self):
        self.browser = webdriver.Remote("http://selenium:4444/wd/hub",
                                        options=self.options,
                                        desired_capabilities=DesiredCapabilities.CHROME.copy())
        advertising_urls = self.get_advertising_urls()
        [self.get_advertising_info(page) for page in advertising_urls]
        self.browser.quit()

    def get_advertising_urls(self):
        self.browser.get(str(self.scrape_url / 'js'))
        time.sleep(np.random.uniform(1.0, 1.5))
        elements = self.get_urls_on_page(str(self.scrape_url))
        i = 1
        while len(elements) < self.max_advertising + self.error_buffer:
            i += 1

            url = f"{self.scrape_url}?{self.page}={i}"
            elements += self.get_urls_on_page(url)

        return elements

    def get_urls_on_page(self, url):
        logger.info(f'Getting add: {url}')
        self.browser.get(url)
        time.sleep(np.random.uniform(1.0, 1.5))

        inner_html = self.browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(inner_html, 'lxml')

        elements = list(
            set(link.get('href') for link in
                soup.findAll('a', attrs={'href': re.compile(f"^{self.language}/detail/")})))
        return elements

    def get_advertising_info(self, advertising_url):
        try:
            url = f"{str(self.scrape_url.parent.parent.parent).replace('/en', '')}{advertising_url}"
            logger.info(f'Scraping: {url}')
            self.browser.get(url)
            time.sleep(np.random.uniform(1.0, 1.5))
            inner_html = self.browser.execute_script("return document.body.innerHTML")
            soup = BeautifulSoup(inner_html, 'lxml')
            params_tag = soup.find('div', {'class': 'params clear'})
            params = {}
            for item in params_tag.findAll('li'):
                param = re.split('\\n+', item.text.strip())
                # it is supposed that all area values are in square meters
                param = [self.strip_accents(p) for p in param]
                if len(param) > 1:
                    params[param[0].lower().replace(' ', '_').replace(':', '')] = param[1].replace(u'\xa0',
                                                                                                   u' ').lower()
                else:
                    params[param[0].lower().replace(' ', '_').replace(':', '')] = any(
                        [True if "'boolean-true'" in i.attrs['ng-if'] else False
                         for i in item.findAll('span')]
                    )
            title_loc = re.split('\\n+', soup.find('div', {'class': 'property-title'}).findAll('h1')[0].text)[1:3]

            if 'total_price' in params:
                price = params['total_price']
            elif 'price' in params:
                price = params['price']
            else:
                price = params['discounted']
            self.db.insert_one(AdvertisingModel(**{'id': advertising_url.split('/')[-1],
                                                   'title': title_loc[0].replace(u'\xa0', u' '),
                                                   'location': title_loc[1].replace(u'\xa0', u' '),
                                                   'price': price,
                                                   'living_area': params['usable_area'] if 'usable_area' in params else
                                                   params[
                                                       'floorage'],
                                                   'reality_type': self.reality_type,
                                                   'building_type': params[
                                                       'building'] if 'building' in params else None,
                                                   'deal_type': self.deal_type,
                                                   'images':
                                                       [i.attrs['src'] for i in
                                                        soup.findAll('img', {'class': 'ob-c-gallery__img'})
                                                        if
                                                        'src' in i.attrs],
                                                   'url': url,
                                                   'created_at': datetime.datetime.now(datetime.timezone.utc),
                                                   'updated_at': datetime.datetime.now(datetime.timezone.utc)
                                                   }))
        except AttributeError as err:
            logger.warning(err)
            return None
        except WebDriverException as err:
            logger.warning(err)
            return None
        except TypeError as err:
            logger.warning(err)
            return None

    @staticmethod
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')


if __name__ == '__main__':
    scraper = RealityScraper(max_advertising=20)
    scraper()
