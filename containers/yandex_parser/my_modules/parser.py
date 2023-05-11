import logging
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import datetime

#Заходим на страницу
def loadPage(yandex_url):
    logging.info('Start Load Page..')
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    logging.info('Initialized virtual display..')
    options = FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")

    browser = webdriver.Firefox(options=options)
    logging.info('Initialized webdriver..')
    if (browser):
        browser.get(yandex_url+'/reviews')
        time.sleep(5)
        logging.info('Accessed %s ..', yandex_url+'/reviews')
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
    #display.stop()
    if 'result' in locals():
        return result

#Получить автора отзыва
def getAutor(review):
    div_autor = review.find(attrs={"class":{"business-review-view__author"}})
    if (div_autor):
        name = review.find(attrs={"itemprop":{"name"}})
        if (name.contents):
            return name.contents[0]
        else:
            return False
    else:
        return False

#Получить рейтинг
def getRating(review):
    ratingValue = review.find(attrs={"itemprop":{"ratingValue"}})
    if (ratingValue):
        return ratingValue['content']

#Получить дату
def getDate(review):
    dateContainer = review.find(attrs={"class":{"business-review-view__date"}})
    if (dateContainer):
        datePublished = review.find(attrs={"itemprop":{"datePublished"}})
        if (datePublished):
            date = datetime.datetime.strptime(datePublished['content'],"%Y-%m-%dT%H:%M:%S.%fZ")
            if date:
                return date.strftime('%d.%m.%Y %H:%M:%S')
            else:
                return False

#Получить текст отзыва
def getText(review):
    text = review.find(attrs={"class":{"business-review-view__body-text"}})
    if (text):
        if (text.contents):
            return text.contents[0]
        else:
            return ''
    else:
        return ''

#Проверить есть ли ответ на отзыв
def checkAnswer(review):
    answer = review.find(attrs={"class":{"business-review-view__comment-expand"}})
    if (answer):
        return True
    else:
        return False
    
#Парсим данные
def grap(html):
    results = []
    soup = BeautifulSoup(html, "html.parser")
    if (soup):
        review_container = soup.find(attrs={"class":{"business-reviews-card-view__reviews-container"}})
        if (review_container):
            reviews = review_container.find_all(attrs={"class":{"business-reviews-card-view__review"}})
            if (reviews):
                for review in reviews:
                    info = {
                        'author': getAutor(review),
                        'rating': getRating(review),
                        'date': getDate(review),
                        'text': getText(review),
                        'answer': checkAnswer(review),
                    }
                    results.append(info)
    return results