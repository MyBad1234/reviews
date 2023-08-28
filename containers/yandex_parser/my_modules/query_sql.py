import os
import pymysql
import json
import time
import sqlalchemy

from .exceptions import SelectExceptions, UpdateExceptions, InsertExceptions, ProxyError


# is docker or no
DOCKER = int(os.environ.get('DOCKER'))

# status of task
STATUS = {
    'created': 1,
    'in_process': 2,
    'done': 3,
    'error': 4,
    'repeat': 5
}

# массив с типами
TYPE = {
    'find_yandex_reviews': 6,
    'save_reviews': 7,
    'python_parser': 9
}

# control db
if DOCKER:
    DB_HOST = os.environ.get('DB_HOST')
    DB_LOGIN = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_DATABASE')
else:
    DB_HOST = 'localhost'
    DB_LOGIN = 'root'
    DB_PASS = ''
    DB_NAME = 'rating'

DB_CHARSET = 'utf8mb4'


def control_count_json(sql, id_result_db: int):
    """control count of JSON objects in queue_yandex_reviews_in_filial"""

    query = "SELECT data FROM queue_yandex_reviews_in_filial WHERE queue_id = %s"
    query = query % (str(id_result_db), )

    sql, data = select_query(sql, query)

    # decode json to dict
    data_dict = json.loads(data[0])
    print(len(data_dict))

    return sql


def repeat_filial(sql, filial_id):
    """control count of filial in db"""

    # make query
    query = "SELECT * FROM queue WHERE status_id = %s AND type_id = %s AND resource_id = %s"
    query = query % (str(STATUS.get('done')), str(TYPE.get('python_parser')), str(filial_id))

    # get data
    sql, data_from_query = select_query(sql, query)

    # control count
    if data_from_query is not None:
        return sql, True

    return sql, False


# connect to db
def connect():
    print('new connection')
    return pymysql.connect(host=DB_HOST, user=DB_LOGIN, password=DB_PASS, database=DB_NAME, charset=DB_CHARSET)


def select_query(sql: pymysql.connections.Connection, query: str, attempt=0, close_connection=None):
    """universal select query"""

    if attempt == 10:
        raise SelectExceptions()

    try:
        with sql.cursor() as cursor:
            # get data
            cursor.execute(query)
            data = cursor.fetchone()

            # save changes in db
            sql.commit()

    except pymysql.err.OperationalError:
        sql, data = select_query(connect(), query, attempt + 1, sql)

    # close old connection
    if close_connection is not None:
        close_connection.close()

    return sql, data


def update_query(sql: pymysql.connections.Connection, query: str, attempt=0, close_connection=None):
    """universal update query"""

    if attempt == 10:
        raise UpdateExceptions()

    try:
        with sql.cursor() as cursor:
            cursor.execute(query)
            sql.commit()

    except pymysql.err.OperationalError:
        sql = update_query(connect(), query, attempt + 1, sql)

    # close old connection
    if close_connection is not None:
        close_connection.close()

    return sql


def insert_query(sql: pymysql.connections.Connection, query: str, attempt=0, close_connection=None):
    """universal insert query"""

    if attempt == 10:
        raise InsertExceptions()

    try:
        with sql.cursor() as cursor:
            cursor.execute(query)
            sql.commit()

            update_id = cursor.lastrowid
    except pymysql.err.OperationalError:
        sql, update_id = insert_query(connect(), query, attempt + 1, sql)

    if close_connection is not None:
        close_connection.close()

    return sql, update_id


def add_result(sql, queue_id, data_json):
    """Добавить результат (Боря)"""

    # connect to db from sqlalchemy
    connect_str = ("mysql+pymysql://" + DB_LOGIN + ":" + DB_PASS + "@"
                   + DB_HOST + "/" + DB_NAME)

    engine = sqlalchemy.create_engine(connect_str, echo=True)

    # model for db
    metadata_obj = sqlalchemy.MetaData()
    data_model = sqlalchemy.Table(
        'queue_yandex_reviews_in_filial',
        metadata_obj,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column('queue_id', sqlalchemy.Integer),
        sqlalchemy.Column('data', sqlalchemy.JSON, nullable=True)
    )

    with engine.connect() as conn:
        # push data to db(get id)
        query = sqlalchemy.insert(data_model).values(queue_id=queue_id, data=data_json)

        result = conn.execute(query)
        conn.commit()

        print(result.inserted_primary_key[0])

        # work with data
        query = sqlalchemy.select(data_model).where(data_model.c.id == result.inserted_primary_key[0])
        for i in conn.execute(query):
            inserted_data = i[2]

        query = sqlalchemy.select(data_model).where(data_model.c.id != result.inserted_primary_key[0])

        for_duplicate = False
        for i in conn.execute(query):
            if inserted_data == i[2]:
                for_duplicate = True

        # update the data if there is a duplicate
        if for_duplicate:
            query = sqlalchemy.update(data_model).where(data_model.c.id == result.inserted_primary_key[0]) \
                .values(data=None)

            conn.execute(query)
            conn.commit()
            print('hz')

    return sql, result.inserted_primary_key


def set_value(sql, table, column, value, where):
    """Записать значения (Боря)"""

    # make sql query
    query = "UPDATE " + table + " set " + column + " = '" + value + "' WHERE " + where

    return update_query(sql, query)


def getFindFilialQueue(sql, type_id):
    """get task from queue"""

    query = ("SELECT `id`, `resource_id` FROM `queue` WHERE `status_id` = %s "
             "AND `type_id`= %s ORDER BY `created` ASC, `priority` ASC LIMIT 1")

    query = query % (str(STATUS['created']), str(type_id))
    sql, data = select_query(sql, query)

    # control data
    if data:
        return sql, {'queue_id': data[0], 'resource_id': data[1]}
    else:
        return sql, False
            

def get_proxy(sql):
    """get proxy for use"""

    # get proxy
    query = ("SELECT `ip`, `login`, `password`, `id` FROM `proxy` WHERE `date_off` "
             "> " + str(int(time.time())) + " AND `connect_type_id` = 2 ORDER BY "
             "`last_active` ASC LIMIT 1")

    sql, data = select_query(sql, query)

    # control data
    if data is None:
        raise ProxyError()

    # update last time for proxy
    query = "UPDATE proxy SET last_active = %s WHERE ip = '%s'"
    query = query % (str(int(time.time())), data[0])

    sql = update_query(sql, query)
    return sql, data


#Получить URL на яндекс картах
def getYandexUrl(sql, resource_id):

    query = "SELECT `name`, `yandex_url` FROM `itemcampagin` WHERE id = %s"
    query = query % (str(resource_id), )

    sql, data = select_query(sql, query)
    return sql, data[1], data[0]


def newQueue(sql, entity_id, resource_id, type_id):
    """Создать новую задачу (Боря)"""

    query = ("INSERT INTO `queue` (`entity_id`, `resource_id`, "
             "`type_id`, `status_id`, `created`, `updated`) values (%s,%s,%s,%s,%s,%s)")

    query_data = (str(entity_id), str(resource_id), str(type_id),
                  str(STATUS['created']), str(int(time.time())), str(int(time.time())))

    query = query % query_data
    return insert_query(sql, query)


def newSaveFilialQueue(sql, entity_id, resource_id):
    """Создать новую задачу "Сохранить отзывы (Боря)"""

    return newQueue(sql, entity_id, resource_id, TYPE['save_reviews'])
    

def statusCreated(sql, queue_id):
    """Ставим статус задачи - 'новый' (Боря)"""

    new_sql = set_value(sql, 'queue', 'status_id', str(STATUS['created']), 'id='+str(queue_id))
    new_sql = set_value(new_sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

    return new_sql


# Ставим статус задачи - "в работе"
def statusInProcess(sql, queue_id):
    new_sql = set_value(sql, 'queue', 'status_id', str(STATUS['in_process']), 'id='+str(queue_id))
    new_sql = set_value(new_sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

    return new_sql


def statusDone(sql, queue_id):
    """Ставим статус задачи - 'готово' (Боря)"""
    sql = checkConnect(sql)
    if sql:
        new_sql = set_value(sql, 'queue', 'status_id', str(STATUS['done']), 'id='+str(queue_id))
        new_sql = set_value(new_sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

        return new_sql


def statusError(sql, queue_id, error_text):
    """Ставим статус задачи - 'ошибка' (Боря)"""

    new_sql = set_value(sql, 'queue', 'status_id', str(STATUS['error']), 'id='+str(queue_id))
    new_sql = set_value(new_sql, 'queue', 'updated', str(int(time.time())), 'id='+str(queue_id))

    return new_sql


# Проверяем sql соединение, и возобновляем если оно потеряно
def checkConnect(sql):
    if (sql.open):
        return sql
    else:
        return connect()
