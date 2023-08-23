import os
import time
import json
import requests
import pymysql
import logging
import traceback
import datetime
from my_modules import query_sql, parser, logger
from my_modules.exceptions import ProxyError
from selenium.common.exceptions import WebDriverException

logging.getLogger().setLevel(logging.INFO)


# for test sqlalchemy
import sqlalchemy


def send_message_tg(company_yandex_url: str):
    """send message to tg"""

    # init tg variables
    token = os.environ.get('TG_BOT')
    chat = os.environ.get('TG_CHAT')

    # get part of url
    part_url = company_yandex_url.split('yandex.ru')

    row_tg = (f"Ошибка при получении отзывов \n"
              f"Компания: { part_url } \n"
              f"Дата и время: { datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S') }")

    requests.post(f"https://api.telegram.org/bot{ token }/sendMessage",
                  json={"chat_id": chat, "text": row_tg})


def run():
    print('it is start')

    # connect to db
    try:
        sql = query_sql.connect()
    except pymysql.err.OperationalError:
        print('Error: failed to connect to the database')
        time.sleep(30)

        return

    yandex_url = None

    if sql:
        sql, queue = query_sql.getFindFilialQueue(sql, query_sql.TYPE['python_parser'])
        # queue = {'queue_id': 114849, 'resource_id': 1946}

        if queue:
            print(queue)
            try:
                # get proxy
                sql, proxy_dict = query_sql.get_proxy(sql)

                # Если есть задача - присваиваем статус "в работе"
                sql = query_sql.statusInProcess(sql, queue['queue_id'])
                sql, yandex_url = query_sql.getYandexUrl(sql, queue['resource_id'])
                if yandex_url:
                    # Получаем страницу
                    html = parser.loadPage(yandex_url, {'ip': proxy_dict[0], 'port': '1050'})
                    if html:
                        # Парсим данные
                        result = parser.grap(html)
                        if result:
                            # Преобразуем в json
                            json_string = json.dumps(result, ensure_ascii=False)
                            if json_string:
                                # Если получили json статус задачи "готово"
                                sql = query_sql.statusDone(sql, queue['queue_id'])
                                # Получаем id записи результата
                                sql, result_id = query_sql.add_result(sql, queue['queue_id'], result)
                                # Создаём задачу на сохранение отзывов
                                sql, result_id = query_sql.newSaveFilialQueue(sql, entity_id=queue['resource_id'],
                                                                              resource_id=result_id)

                                # control count of reviews
                                sql = query_sql.control_count_json(sql, queue['queue_id'])
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

            # Если получили ошибку драйвера, данная задача получает статус новой и делаем паузу 10 минут
            except WebDriverException:
               if queue['queue_id']:
                   sql = query_sql.statusError(sql, queue['queue_id'], 'hz')

            except ProxyError:
                print('proxy error')
                time.sleep(300)

            except Exception as error:
                print(traceback.format_exc())
                if queue['queue_id']:
                    error_text = "Ошибка:" + str(repr(error))
                    logger.errorLog(error_text)
                    query_sql.statusError(sql, queue['queue_id'], error_text)

                # send message
                if yandex_url:
                    send_message_tg(yandex_url)

        else:
            print('пауза')
            time.sleep(300)

        try:
            sql.close()
        except pymysql.err.Error:
            pass


def test():
    engine = sqlalchemy.create_engine(
        "mysql+pymysql://nikrbk_geo_test:zuJDfrKYLzbvnNs3V6PB@nikrbk.beget.tech/nikrbk_geo_test", echo=True)

    metadata_obj = sqlalchemy.MetaData()
    data_table = sqlalchemy.Table(
        'queue_reviews_in_filial',
        metadata_obj,
        sqlalchemy.Column('queue_id', sqlalchemy.Integer),
        sqlalchemy.Column('data', sqlalchemy.JSON)
    )

    with engine.connect() as conn:
        stmp = sqlalchemy.insert(data_table).values(queue_id=109959, data={'lol': '\nlol"'})
        conn.execute(stmp)

        conn.commit()


while True:
    run()
