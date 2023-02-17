import logging

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
logging.getLogger().setLevel(logging.INFO)

BASE_URL = 'https://yandex.ru/maps/org/76850668350/reviews'
PROXY_IP = '45.87.253.104'
PROXY_USERNAME = 'n9Op25'
PROXY_PASSWORD = 'P3FUETNdBI'
PROXY_PORT = '1051'
proxy_access = PROXY_USERNAME+':'+PROXY_PASSWORD+'@'+PROXY_IP+':'+PROXY_PORT
"""
options = {
'proxy': {
    'http': 'http://'+proxy_access,
    'https': 'https://'+proxy_access,
    'socks5': 'socks5://'+proxy_access,
    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
    }
}
"""
proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': PROXY_IP+':'+PROXY_PORT,
    'ftpProxy': PROXY_IP+':'+PROXY_PORT,
    'sslProxy': PROXY_IP+':'+PROXY_PORT,
    'socks5': PROXY_IP+':'+PROXY_PORT,
    'socksUsername': PROXY_USERNAME,
    'socksPassword': PROXY_PASSWORD
    })


def firefox_example():
    display = Display(visible=0, size=(800, 600))
    display.start()
    logging.info('Initialized virtual display..')

    logging.info('Prepared firefox profile..')

    browser = webdriver.Firefox(proxy=proxy)
    logging.info('Initialized firefox browser..')

    browser.get(BASE_URL)
    logging.info('Accessed %s ..', BASE_URL)

    logging.info('Page title: %s', browser.title)

    browser.quit()
    display.stop()

firefox_example()