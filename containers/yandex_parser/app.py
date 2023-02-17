import logging
import time
import json
from my_modules import query_sql, parser, logger
from selenium.common.exceptions import WebDriverException

logging.getLogger().setLevel(logging.INFO)

def run():
    sql = query_sql.connect()
    if (sql):
        queue = query_sql.getFindFilialQueue(sql, query_sql.TYPE['find_yandex_reviews'])
        if (queue):
            try:
                #Если есть задача - присваиваем статус "в работе"
                query_sql.statusInProcess(sql, queue['queue_id'])
                yandex_url = query_sql.getYandexUrl(sql, queue['resource_id'])
                if (yandex_url):
                    #Получаем страницу
                    html = parser.loadPage(sql, yandex_url)
                    if (html):
                        #Парсим данные
                        result = parser.grap(html)
                        if (result):
                            #Преобразуем в json
                            json_string = json.dumps(result, ensure_ascii=False)
                            if (json_string):
                                #Если получили json статус задачи "готово"
                                query_sql.statusDone(sql, queue['queue_id'])
                                #Получаем id записи результата
                                result_id = query_sql.addResult(sql, queue['queue_id'], json_string)
                                #Создаём задачу на сохранение отзывов
                                query_sql.newSaveFilialQueue(sql, entity_id=queue['resource_id'], resource_id=result_id)
                            else:
                                query_sql.statusError(sql, queue['queue_id'], 'Ошибка получения json')
                        else:
                            logger.errorLog("Ошибка в парсере")
                            query_sql.statusError(sql, queue['queue_id'], 'Не получены данные со страницы')
                    else:
                        logger.errorLog("Не получена страница")
                        query_sql.statusError(sql, queue['queue_id'], 'Не получена страница')
                else:
                    query_sql.statusError(sql, queue['queue_id'], 'Нет URL филиала')
            #Если получили ошибку драйвера, данная задача получает статус новой и делаем паузу 10 минут
            except WebDriverException:
                if (queue['queue_id']):
                    query_sql.statusCreated(sql, queue['queue_id'])
            except Exception as error:
                if (queue['queue_id']):
                    error_text = "Ошибка:"+str(repr(error))
                    logger.errorLog(error_text)
                    query_sql.statusError(sql, queue['queue_id'], error_text)
        else:
            print('пауза')
            time.sleep(300)
        sql.close()

while True:
    run()