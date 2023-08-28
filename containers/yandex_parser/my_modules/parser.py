import logging
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import datetime


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


def get_some_reviews(browser, for_loading=0, for_now=0):
    """get 30 reviews with answer"""

    # get all elements with review
    review_elements = browser.find_elements(
        by=By.CSS_SELECTOR, value='.business-reviews-card-view__review'
    )

    # parse elements
    for_js = 0
    for i in review_elements:
        if (for_js >= for_now) and (for_js < 30):
            # scroll to review
            browser.execute_script("document.querySelectorAll('.business-reviews-card-view__review')"
                                   "[" + str(for_js) + "].scrollIntoView({block: 'center'})")

            # control answer
            answer_is_present = browser.execute_script("return document.querySelectorAll('"
                                                       ".business-reviews-card-view__review')"
                                                       "[" + str(for_js) + "].querySelector('"
                                                       ".business-review-view__reactions-container')"
                                                       ".children.length")

            if answer_is_present == 2:

                # find btn for get answer and click to it
                all_div = i.find_element(by=By.CSS_SELECTOR, value='.business-review-view__reactions-container') \
                    .find_elements(by=By.CSS_SELECTOR, value='div')

                for j in all_div:
                    correct_div = j

                correct_div.click()

        if ((for_js % 10) == 0) and (for_js < 30):
            time.sleep(2)

        for_js += 1

    # control count
    time.sleep(3)

    review_elements = browser.find_elements(
        by=By.CSS_SELECTOR, value='.business-reviews-card-view__review'
    )

    count_elements = 0
    for i in review_elements:
        count_elements += 1

    if (for_loading != count_elements) and (for_js < 30):
        get_all_reviews(browser, count_elements, for_js)


def get_all_reviews(browser, for_loading=0, for_now=0):
    """get all reviews with answer"""

    # get all elements with review
    review_elements = browser.find_elements(
        by=By.CSS_SELECTOR, value='.business-reviews-card-view__review'
    )

    # parse elements
    for_js = 0
    for i in review_elements:
        if for_js >= for_now:

            # scroll to review
            browser.execute_script("document.querySelectorAll('.business-reviews-card-view__review')"
                                   "[" + str(for_js) + "].scrollIntoView({block: 'center'})")

            # control answer
            answer_is_present = browser.execute_script("return document.querySelectorAll('"
                                                       ".business-reviews-card-view__review')"
                                                       "[" + str(for_js) + "].querySelector('"
                                                       ".business-review-view__reactions-container')"
                                                       ".children.length")

            if answer_is_present == 2:

                # find btn for get answer and click to it
                all_div = i.find_element(by=By.CSS_SELECTOR, value='.business-review-view__reactions-container') \
                    .find_elements(by=By.CSS_SELECTOR, value='div')

                for j in all_div:
                    correct_div = j

                correct_div.click()

        if (for_js % 10) == 0:
            time.sleep(2)

        for_js += 1

    # control count
    time.sleep(3)

    review_elements = browser.find_elements(
        by=By.CSS_SELECTOR, value='.business-reviews-card-view__review'
    )

    count_elements = 0
    for i in review_elements:
        count_elements += 1

    if for_loading != count_elements:
        get_all_reviews(browser, count_elements, for_js)


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

    logging.info('Initialized webdriver..')
    if browser:
        browser.get(yandex_url+'/reviews')
        time.sleep(5)
        logging.info('Accessed %s ..', yandex_url+'/reviews')
        sort = browser.find_element(By.CSS_SELECTOR,  '.rating-ranking-view')
        if sort:
            sort.click()
            time.sleep(5)
            sort_options = browser.find_elements(By.CSS_SELECTOR,  '.rating-ranking-view__popup-line')
            if sort_options:
                for option in sort_options:
                    title = option.get_attribute("aria-label")
                    if title == 'По новизне':
                        option.click()
                        break
                time.sleep(5)

                # get all reviews
                if repeat:
                    get_some_reviews(browser)
                else:
                    get_all_reviews(browser)

                result = browser.page_source

    browser.quit()
    # display.stop()

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


def get_answer_text(review):
    div_answer = review.find(attrs={"class":{"business-review-comment__bubble"}})

    if div_answer:
        return div_answer.text
    else:
        return False


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
                        'author': getAutor(review),
                        'rating': getRating(review),
                        'date': getDate(review),
                        'text': getText(review),
                        'answer': checkAnswer(review),
                        'answer_text': get_answer_text(review)
                    }
                    results.append(info)

                    for_count += 1

    return replace_symbols(results)
