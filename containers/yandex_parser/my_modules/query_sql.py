import pymysql
import time
import json

#Режим в контейнере
DOCKER = True

#Массив со статусами
STATUS = {
    'created': 1,
    'in_process': 2,
    'done': 3,
    'error': 4,
    'repeat': 5
}

#массив с типами
TYPE = {
    'find_yandex_reviews':6,
    'save_reviews':7,
    'python_parser':9
}

#Настройки БД
if DOCKER:
    DB_HOST = 'nikrbk.beget.tech'
    DB_LOGIN = 'nikrbk_geo_test'
    DB_PASS = 'zuJDfrKYLzbvnNs3V6PB'
    DB_NAME = 'nikrbk_geo_test'
else:
    DB_HOST = 'localhost'
    DB_LOGIN = 'root'
    DB_PASS = ''
    DB_NAME = 'rating'
DB_CHARSET = 'utf8mb4'

#Подключаемся к mysql
def connect():
    con = pymysql.connect(host=DB_HOST, user=DB_LOGIN, password=DB_PASS, database=DB_NAME, charset=DB_CHARSET)
    if con:
        return con
    else:
        return False
    
#Получить задание из очереди
def getFindFilialQueue(sql, type_id):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            cursor.execute("SELECT `id`, `resource_id` FROM `queue` WHERE `status_id` = "+str(STATUS['created'])+" AND `type_id`= "+str(type_id)+" ORDER BY `created` ASC, `priority` ASC LIMIT 1")
            queue = cursor.fetchone()
            sql.commit()
            if (queue):
                return {
                    'queue_id':queue[0],
                    'resource_id':queue[1],
                }
            else:
                print('not finded queue')
                return False
            
#Получить прокси
def getProxy(sql):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            cursor.execute("SELECT `ip`, `login`, `password`, `id` FROM `proxy` WHERE `date_off` > "+str(int(time.time()))+" ORDER BY `last_active` ASC LIMIT 1")
            proxy = cursor.fetchone()
            sql.commit()
            if (proxy):
                return {
                    'ip':proxy[0],
                    'login':proxy[1],
                    'password':proxy[2],
                    'id':proxy[3],
                }
            else:
                print('not finded proxy')
                return False
            
#Получить URL на яндекс картах
def getYandexUrl(sql, resource_id):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            cursor.execute("SELECT `yandex_url` FROM `itemcampagin` WHERE id ="+str(resource_id))
            yandex_url = cursor.fetchone()
            sql.commit()
            return yandex_url[0]
        
#Добавить результат
def addResult(sql, queue_id, data):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            query = "INSERT INTO `queue_reviews_in_filial` (`queue_id`, `data`) values (%s,%s)"
            cursor.execute(query,(str(queue_id),str(data)))
            sql.commit()
            return cursor.lastrowid

#Создать новую задачу
def newQueue(sql, entity_id, resource_id, type_id):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            query = "INSERT INTO `queue` (`entity_id`, `resource_id`, `type_id`, `status_id`, `created`, `updated`) values (%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (str(entity_id), str(resource_id), str(type_id), str(STATUS['created']), str(int(time.time())), str(int(time.time()))))
            sql.commit()

#Записать значение
def setValue(sql, table, column, value, where):
    sql = checkConnect(sql)
    if (sql):
        with sql.cursor() as cursor:
            query = "UPDATE "+table+" set "+column+" = '"+value+"' WHERE "+where
            cursor.execute(query)
            sql.commit()
         
#Создать новую задачу "Сохранить отзывы"
def newSaveFilialQueue(sql, entity_id, resource_id):
    sql = checkConnect(sql)
    if (sql):
        newQueue(sql, entity_id, resource_id, TYPE['save_reviews'])
    
#Ставим статус задачи - "новый"
def statusCreated(sql, queue_id):
    sql = checkConnect(sql)
    if (sql):
        setValue(sql, 'queue', 'status_id', str(STATUS['created']), 'id='+str(queue_id))
        setValue(sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))
    
#Ставим статус задачи - "в работе"
def statusInProcess(sql, queue_id):
    sql = checkConnect(sql)
    if (sql):
        setValue(sql, 'queue', 'status_id', str(STATUS['in_process']), 'id='+str(queue_id))
        setValue(sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

#Ставим статус задачи - "готово"
def statusDone(sql, queue_id):
    sql = checkConnect(sql)
    if (sql):
        setValue(sql, 'queue', 'status_id', str(STATUS['done']), 'id='+str(queue_id))
        setValue(sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))
    
#Ставим статус задачи - "ошибка"
def statusError(sql, queue_id, error_text):
    sql = checkConnect(sql)
    if (sql):
        setValue(sql, 'queue', 'status_id', str(STATUS['error']), 'id='+str(queue_id))
        #setValue(sql, 'queue', 'error_log', str(json.dumps(error_text, ensure_ascii=False)), 'id='+str(queue_id))
        setValue(sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

#Проверяем sql соединение, и возобновляем если оно потеряно 
def checkConnect(sql):
    if (sql.open):
        return sql
    else:
        return connect()