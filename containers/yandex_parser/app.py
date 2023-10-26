import os
import time
import json
import requests
import datetime
import pymysql
import logging
import traceback
import datetime

import selenium.common.exceptions

from my_modules import query_sql, parser, logger
from my_modules.exceptions import ProxyError
from selenium.common.exceptions import WebDriverException

# for test sqlalchemy
import sqlalchemy

logging.getLogger().setLevel(logging.INFO)


def send_message_tg(queue_id=None, company=None, filial=None, url=None):
    """send message to tg"""

    # control thread for theme of group
    thread_id = os.environ.get('THREAD_GROUP_GOOD')

    # control server name (None or no)
    server_name = os.environ.get('SERVER_NAME')
    if server_name is None:
        server_name = 'неизвестно'

    # work with task
    if queue_id is not None:
        data = {
            'task': queue_id,
            'company': company,
            'filial': filial,
            'url': url
        }
    else:
        data = {
            'task': 'неизвестно',
            'company': 'неизвестно',
            'filial': 'неизвестно',
            'url': 'неизвестно'
        }

    # get params for send message to tg
    token = os.environ.get('TG_BOT')
    chat = os.environ.get('TG_CHAT')

    row_tg = (f"Ошибка при парсинге отзывов #{data.get('task')}\n"
              f"Компания: {data.get('company')}\n"
              f"Филиал: {data.get('filial')}\n"
              f"Ссылка: {data.get('url')}")

    if thread_id is None:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": int(chat), "text": row_tg})

    else:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": int(chat), "text": row_tg, 'message_thread_id': int(thread_id)})


def run():
    print('it is start')
    dt_now = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    print(dt_now)

    # connect to db
    try:
        sql = query_sql.connect()
    except pymysql.err.OperationalError:
        print('Error: failed to connect to the database')
        time.sleep(10)

        return

    yandex_url = None
    organization = None
    id_filial = None
    queue = None

    if sql:
        sql, queue = query_sql.getFindFilialQueue(sql, query_sql.TYPE['python_parser'])
        # queue = {'queue_id': 131008, 'resource_id': 2088}

        if queue:
            id_filial = queue.get('resource_id')
            print(queue)
            try:
                # get proxy
                sql, proxy_dict = query_sql.get_proxy(sql)

                # Если есть задача - присваиваем статус "в работе"
                sql = query_sql.statusInProcess(sql, queue['queue_id'])
                sql, yandex_url, organization = query_sql.getYandexUrl(sql, queue['resource_id'])

                if yandex_url:
                    # control count of repeat
                    sql, control_repeat = query_sql.repeat_filial(sql, queue['resource_id'])

                    # Получаем страницу
                    html, r_data = parser.load_page(yandex_url, {'ip': proxy_dict[0], 'port': '1050'}, control_repeat)

                    # update reting
                    sql = query_sql.update_rating(sql, str(queue.get('resource_id')), **r_data)
                    if html:
                        # Парсим данные
                        result = parser.grap(html, control_repeat)
                        if result:
                            # Преобразуем в json
                            json_string = json.dumps(result, ensure_ascii=False)
                            if json_string:
                                # Если получили json статус задачи "готово"
                                sql = query_sql.statusDone(sql, queue['queue_id'])
                                # Получаем id записи результата
                                sql, result_id = query_sql.add_result(sql, queue['queue_id'], json_string)

                                print(f'id_result: {result_id}')

                                # Создаём задачу на сохранение отзывов
                                sql, result_id = query_sql.newSaveFilialQueue(sql, entity_id=queue['resource_id'],
                                                                              resource_id=queue['queue_id'])

                                print(f'repeat: {str(control_repeat)}')
                                time.sleep(20)

                            else:
                                sql = query_sql.statusError(sql, queue['queue_id'], 'Ошибка получения json')
                        else:
                            logger.errorLog("Ошибка в парсере")
                            sql = query_sql.statusError(sql, queue['queue_id'], 'Не получены данные со страницы')
                    else:
                        logger.errorLog("Не получена страница")
                        sql = query_sql.statusError(sql, queue['queue_id'], 'Не получена страница')
                else:
                    sql = query_sql.statusError(sql, queue['queue_id'], 'Нет URL филиала')

            except ProxyError:
                print('proxy error')
                time.sleep(300)

            except Exception as error:
                print(traceback.format_exc())
                if queue['queue_id']:
                    error_text = "Ошибка:" + str(repr(error))
                    logger.errorLog(error_text)
                    query_sql.statusError(sql, queue['queue_id'], error_text)

                # write log to error file
                error_obj = logger.ErrorClass()
                error_obj.write_error(queue, traceback.format_exc())

                # send message
                send_message_tg(queue_id=queue.get('queue_id'),
                                company=organization,
                                filial=id_filial,
                                url=yandex_url)

        else:
            print('пауза')
            time.sleep(20)

        try:
            sql.close()
        except pymysql.err.Error:
            pass


run()
