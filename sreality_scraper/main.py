import re
import time
from pathlib import Path
from typing import List

import numpy as np

import unicodedata
from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.safari.options import Options
# from joblib import Parallel, delayed


class AdvertisingModel(BaseModel):
    id: int
    price: str
    living_area: str
    reality_type: str
    building_type: str
    deal_type: str
    images: List[str]
    url: str


class RealityScraper:
    def __init__(self, reality_type: str = 'apartments', deal_type: str = 'for-sale', max_advertising: int = 500):
        self.page = 'page'
        self.language = '/en'
        self.search = 'search'
        self.base_url = Path(f'https://www.sreality.cz{self.language}/{self.search}')
        self.reality_type = reality_type
        self.deal_type = deal_type
        self.max_advertising = max_advertising
        self.scrape_url = self.base_url / deal_type / reality_type
        self.reality_type = reality_type
        options = Options()
        options.add_argument('--headless')
        self.browser = webdriver.Safari(options=options)

    def __call__(self):
        advertising_urls = self.get_advertising_urls()
        # prices = Parallel(n_jobs=-1)(delayed(self.get_advertising_info)(page) for page in advertising_urls)
        prices = [self.get_advertising_info(page) for page in advertising_urls]
        self.browser.quit()
        return prices

    def get_advertising_urls(self):
        self.browser.get(str(self.scrape_url / 'js'))
        time.sleep(np.random.uniform(1.0, 1.5))
        elements = self.get_urls_on_page(str(self.scrape_url))
        i = 1
        while len(elements) < self.max_advertising:
            i += 1

            url = f"{self.scrape_url}?{self.page}={i}"
            elements += self.get_urls_on_page(url)

        return elements

    def get_urls_on_page(self, url):
        self.browser.get(url)
        time.sleep(np.random.uniform(1.0, 1.5))

        inner_html = self.browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(inner_html, 'lxml')

        elements = list(
            set(link.get('href') for link in
                soup.findAll('a', attrs={'href': re.compile(f"^{self.language}/detail/")})))
        return elements

    def get_advertising_info(self, advertising_url):

        url = f"{str(self.scrape_url.parent.parent.parent).replace('/en', '')}{advertising_url}"

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
                params[param[0].lower().replace(' ', '_').replace(':', '')] = param[1].replace(u'\xa0', u' ').lower()
            else:
                params[param[0].lower().replace(' ', '_').replace(':', '')] = any(
                    [True if "'boolean-true'" in i.attrs['ng-if'] else False
                     for i in item.findAll('span')]
                )
        return AdvertisingModel(**{'id': advertising_url.split('/')[-1],
                                   'price': params['total_price'] if 'total_price' in params else params[
                                       'discounted'],
                                   'living_area': params['usable_area'] if 'usable_area' in params else params[
                                       'floorage'],
                                   'reality_type': self.reality_type,
                                   'building_type': params['building'] if 'building' in params else None,
                                   'deal_type': self.deal_type,
                                   'images':
                                       [i.attrs['src'] for i in soup.findAll('img', {'class': 'ob-c-gallery__img'}) if
                                        'src' in i.attrs],
                                   'url': url
                                   })

    @staticmethod
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')


if __name__ == '__main__':
    scraper = RealityScraper(max_advertising=20)
    scraper()
