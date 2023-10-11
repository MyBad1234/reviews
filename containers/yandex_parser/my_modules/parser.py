import logging

import selenium.common.exceptions
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import datetime


def rating_data_main_page(browser: webdriver.Chrome):
    """get data of rating without reviews"""

    # rating
    try:
        rating = browser.find_element(By.CSS_SELECTOR, '.business-summary-rating-badge-view__rating') \
            .text

        rating = rating.split()[1].replace(',', '.')
    except selenium.common.exceptions.NoSuchElementException:
        rating = '0'

    # count of evaluation
    try:
        all_count = browser.find_element(By.CSS_SELECTOR, '.business-summary-rating-badge-view__rating-count') \
            .text

        all_count = all_count.split()[0]
    except selenium.common.exceptions.NoSuchElementException:
        all_count = '0'

    return {
        'rating': rating,
        'all_count': all_count,
        'reviews_count': '0'
    }


def rating_data(browser: webdriver.Chrome):
    """get data of rating"""

    # rating
    try:
        rating = browser.find_element(By.CSS_SELECTOR, '.business-summary-rating-badge-view__rating') \
            .text

        rating = rating.split()[1].replace(',', '.')
    except selenium.common.exceptions.NoSuchElementException:
        rating = '0'

    # count of evaluation
    try:
        all_count = browser.find_element(By.CSS_SELECTOR, '.business-summary-rating-badge-view__rating-count') \
            .text

        all_count = all_count.split()[0]
    except selenium.common.exceptions.NoSuchElementException:
        all_count = '0'

    # count of reviews
    reviews_count = browser.find_element(By.CSS_SELECTOR, '._name_reviews').find_element(By.CSS_SELECTOR, 'div').text

    return {
        'rating': rating,
        'all_count': all_count,
        'reviews_count': reviews_count
    }


def replace_symbols(data_arr: list):
    """work with ' symbols """

    new_arr = []

    for i in data_arr:
        obj = {
            'author': i.get('author').replace('"', "'").replace('\n', '\\n'),
            'rating': i.get('rating'),
            'date': i.get('date'),
            'text': i.get('text').replace('"', "'").replace('\n', '\\n'),
            'answer': i.get('answer'),
        }
        try:
            obj.update({
                'answer_text': i.get('answer_text').replace('"', "'").replace('\n', '\\n')
            })
        except AttributeError:
            obj.update({
                'answer_text': i.get('answer_text')
            })

        new_arr.append(obj)

    return new_arr


def get_some_reviews(browser, count_elements=0, for_js=0):
    """test for reviews"""

    script = ("function get_all_reviews(for_loading=0, for_now=0) {"
              "let review_elements = document.querySelectorAll('.business-reviews-card-view__review'); "
              "let for_js = 0; "
              "for (let i of review_elements) { "
              "if ((for_js > for_now) && (for_js < 30)) { "
              "document.querySelectorAll('.business-reviews-card-view__review')[for_js].scrollIntoView({block: 'center', 'behavior': 'smooth'}); "
              "let answer_is_present = document.querySelectorAll('.business-reviews-card-view__review')[for_js].querySelector('.business-review-view__reactions-container').children.length; "
              "} "
              "for_js += 1; }}"
              "get_all_reviews()")

    browser.execute_script(script)

    time.sleep(3)
    now_elements = browser.execute_script(
        "return document.querySelectorAll('.business-reviews-card-view__review').length")

    if now_elements != count_elements:
        get_all_reviews(browser, now_elements)
    else:
        if for_js < 3:
            get_all_reviews(browser, now_elements, for_js + 1)


def see_all_answer(browser):
    script = ("function lol(elem){ "
              "console.log('wow'); "
              "elem.scrollIntoView({'block': 'center', 'behavior': 'smooth'});"
              "elem.click() " 
              "} "
              "for (let i of document.querySelectorAll('.business-review-view__comment-expand')) { "
              "setTimeout(500, lol(i)); "
              "}")

    browser.execute_script(script)
    time.sleep(10)


def get_all_reviews(browser, count_elements=0, for_js=0):
    """test for reviews"""

    script = ("function get_all_reviews(for_loading=0, for_now=0) {"
              "let review_elements = document.querySelectorAll('.business-reviews-card-view__review'); "
              "let for_js = 0; "
              "for (let i of review_elements) { "
              "if (for_js > for_now) { "
              "document.querySelectorAll('.business-reviews-card-view__review')[for_js].scrollIntoView({block: 'center', 'behavior': 'smooth'}); "
              "let answer_is_present = document.querySelectorAll('.business-reviews-card-view__review')[for_js].querySelector('.business-review-view__reactions-container').children.length; "
              "} "
              "for_js += 1; }}"
              "get_all_reviews()")

    browser.execute_script(script)

    time.sleep(2)
    now_elements = browser.execute_script(
        "return document.querySelectorAll('.business-reviews-card-view__review').length")

    if now_elements != count_elements:
        get_all_reviews(browser, now_elements)
    else:
        if for_js < 3:
            get_all_reviews(browser, now_elements, for_js + 1)


def load_page(yandex_url, proxy: dict, repeat: bool):
    """go to page"""

    logging.info('Start Load Page..')
    # display = Display(visible=0, size=(800, 600))
    # display.start()
    logging.info('Initialized virtual display..')
    options = webdriver.ChromeOptions()

    # set proxy
    proxy_str = proxy.get('ip') + ':' + proxy.get('port')
    options.add_argument('--proxy-server=%s' % proxy_str)

    browser = webdriver.Chrome(options=options)
    result = None

    logging.info('Initialized webdriver..')
    if browser:
        print(yandex_url + '/reviews')
        browser.get(yandex_url + '/reviews')
        time.sleep(3)
        logging.info('Accessed %s ..', yandex_url+'/reviews')

        try:
            sort = browser.find_element(By.CSS_SELECTOR,  '.rating-ranking-view')
        except selenium.common.exceptions.NoSuchElementException:
            r_data = rating_data_main_page(browser)
            sort = None

        if sort:
            sort.click()
            time.sleep(3)
            sort_options = browser.find_elements(By.CSS_SELECTOR,  '.rating-ranking-view__popup-line')
            if sort_options:
                for option in sort_options:
                    title = option.get_attribute("aria-label")
                    if title == 'По новизне':
                        option.click()
                        break
                time.sleep(3)

                # get rating
                r_data = rating_data(browser)

                # get all reviews
                if repeat:
                    get_some_reviews(browser)
                else:
                    get_all_reviews(browser)

                see_all_answer(browser)

                result = browser.page_source

    browser.quit()
    # display.stop()

    return result, r_data


def get_autor(review):
    """get author of response"""

    div_autor = review.find(attrs={"class": {"business-review-view__author"}})
    if div_autor:
        name = review.find(attrs={"itemprop": {"name"}})
        if name.contents:
            return name.contents[0]
        else:
            return ''
    else:
        return ''


def get_answer_text(review):
    div_answer = review.find(attrs={"class": {"business-review-comment-content__bubble"}})

    if div_answer:
        return div_answer.text
    else:
        return ''


# Получить рейтинг
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


def grap(html, repeat):
    """parse data"""

    # init bs4
    results = []
    soup = BeautifulSoup(html, "html.parser")

    # work with bs4
    if soup:
        review_container = soup.find(attrs={"class":{"business-reviews-card-view__reviews-container"}})
        if review_container:
            reviews = review_container.find_all(attrs={"class":{"business-reviews-card-view__review"}})
            if reviews:

                for_count = 0
                for review in reviews:
                    # control count
                    if repeat and (for_count == 30):
                        break

                    # add data to struct
                    info = {
                        'author': get_autor(review),
                        'rating': getRating(review),
                        'date': getDate(review),
                        'text': getText(review),
                        'answer': checkAnswer(review),
                        'answer_text': get_answer_text(review)
                    }
                    results.append(info)

                    for_count += 1

    return results
