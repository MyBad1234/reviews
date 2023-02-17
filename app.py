import logging

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
import time

logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'https://yandex.ru/maps/org/76850668350/reviews'
PROXY_IP = '45.87.253.104'
PROXY_USERNAME = 'n9Op25'
PROXY_PASSWORD = 'P3FUETNdBI'
PROXY_PORT = '1051'

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': PROXY_IP+':'+PROXY_PORT,
    'ftpProxy': PROXY_IP+':'+PROXY_PORT,
    'sslProxy': PROXY_IP+':'+PROXY_PORT,
    'socks5': PROXY_IP+':'+PROXY_PORT,
    'socksUsername': PROXY_USERNAME,
    'socksPassword': PROXY_PASSWORD
    })


def loadPage():
    display = Display(visible=0, size=(800, 600))
    display.start()
    logging.info('Initialized virtual display..')
    options = FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")

    browser = webdriver.Firefox(options=options, proxy=proxy)
    if (browser):
        browser.get(BASE_URL)
        time.sleep(5)
        logging.info('Accessed %s ..', BASE_URL)
        sort = browser.find_element(By.CSS_SELECTOR,  '.rating-ranking-view' )
        if (sort):
            sort.click()
            time.sleep(5)
            sort_options = browser.find_elements(By.CSS_SELECTOR,  '.rating-ranking-view__popup-line' )
            if sort_options:
                for option in sort_options:
                    title = option.get_attribute("aria-label")
                    if (title == 'По новизне'):
                        option.click()
                        break
                time.sleep(5)
                result = browser.page_source

    browser.quit()
    display.stop()
    if 'result' in locals():
        return result

#Парсим данные
def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    if (soup):
        review_container = soup.find(attrs={"class":{"business-reviews-card-view__reviews-container"}})
        if (review_container):
            reviews = review_container.find_all(attrs={"class":{"business-reviews-card-view__review"}})
            if (reviews):
                logging.info(reviews)

page = loadPage()
if (page):
    parse(page)