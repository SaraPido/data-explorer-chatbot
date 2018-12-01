import logging
import mysql.connector
import json

logger = logging.getLogger(__name__)

connection = None
db_properties = None


# Queries

def query_select(query, t):
    cursor = connection.cursor()
    cursor.execute(query, t)
    return cursor.fetchall()


def query_select_on_word(element_type, word):
    """e
    e.g. "SELECT * FROM Teacher WHERE name='"+word+"' OR surname='"+word+"'"
    :param element_type:
    :param word:
    :return: dictionary representing the row
    """
    el_properties = get_element_properties(element_type)
    query_string = "SELECT * FROM {} ".format(el_properties['table_name'])
    word_list = el_properties['word_list']
    if word_list:
        query_string += "WHERE "
        query_string += " OR ".join(["{}=%s".format(w_col) for w_col in word_list])
        rows = query_select(query_string, tuple([word] * len(word_list)))
        return decorate_rows(element_type, rows)
    else:
        pass  # todo: error/exception


def decorate_rows(element_type, rows):
    element = next(filter(lambda el: el['type'] == element_type, db_properties), None)
    if element:
        columns = element['column_list']
        return list(map(lambda r: dict(zip(columns, r)), rows))
    else:
        pass # todo: error/exception


# Database properties

def load_db_properties(db_properties_path):
    global db_properties
    logger.info('Loading database properties...')
    with open(db_properties_path) as f:
        db_properties = json.load(f)
    logger.info('Database properties have been loaded!')
    # logger.info(pformat(db_properties))


def get_element_properties(element_type):
    return next(filter(lambda el: el['type'] == element_type, db_properties), None)


# Connection

def connect():
    global connection
    logger.info('Connecting to the database...')
    connection = mysql.connector.connect(user='rasa', password='rasa', host='127.0.0.1', database='rasa_db')
    logger.info('Connection succeeded!')
    # cnx.close()
