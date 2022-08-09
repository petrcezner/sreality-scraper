import json
import re
import time
from pathlib import Path

import numpy as np

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.safari.options import Options


class RealityScraper:
    def __init__(self, reality_type: str = 'byty', deal_type: str = 'prodej', max_advertising: int = 500):
        self.base_url = Path('https://www.sreality.cz/hledani')
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
        prices = []
        for page in advertising_urls:
            prices.append(self.get_advertising_info(page))

        k = 1
        self.browser.quit()

    def get_advertising_urls(self):
        self.browser.get(str(self.scrape_url / 'js'))
        time.sleep(np.random.uniform(1.0, 1.5))
        elements = self.get_urls_on_page(str(self.scrape_url))
        i = 1
        while len(elements) < self.max_advertising:
            i += 1

            url = f"{self.scrape_url}?strana={i}"
            elements += self.get_urls_on_page(url)

        return elements

    def get_urls_on_page(self, url):
        self.browser.get(url)
        time.sleep(np.random.uniform(1.0, 1.5))

        inner_html = self.browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(inner_html, 'lxml')

        elements = list(
            set(link.get('href') for link in soup.findAll('a', attrs={'href': re.compile("^/detail/")})))
        return elements

    def get_advertising_info(self, advertising_url):

        url = f'{self.scrape_url.parent.parent.parent}{advertising_url}'

        self.browser.get(url)
        time.sleep(np.random.uniform(1.0, 1.5))
        inner_html = self.browser.execute_script("return document.body.innerHTML")
        soup = BeautifulSoup(inner_html, 'lxml')
        params_tag = soup.find('div', {'class': 'params clear'})
        l = 1


if __name__ == '__main__':
    scraper = RealityScraper(max_advertising=20)
    scraper()
