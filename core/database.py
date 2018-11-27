import logging
import mysql.connector

logger = logging.getLogger(__name__)

connection = None


def query_select(query):
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def connect():
    global connection
    logger.info('Connecting to the database...')
    connection = mysql.connector.connect(user='rasa', password='rasa', host='127.0.0.1', database='rasa_db')
    logger.info('Connection succeeded!')
    # cnx.close()
