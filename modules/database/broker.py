import json
import logging
from mysql import connector

from modules.settings import DATABASE_NAME, DB_SCHEMA_PATH, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST

logger = logging.getLogger(__name__)

db_schema = None
connection = None


def connect():
    global connection
    logger.info('Database:\n'
                '"' + DATABASE_NAME + '"')
    logger.info('Connecting to the database...')
    connection = connector.connect(user=DATABASE_USER,
                                   password=DATABASE_PASSWORD,
                                   host=DATABASE_HOST,
                                   database=DATABASE_NAME)
    logger.info('Connection succeeded!')
    # cnx.close()


def load_db_schema():
    global db_schema
    logger.info('Database schema file:\n'
                '"' + DB_SCHEMA_PATH + '"')
    logger.info('Loading database schema file...')
    with open(DB_SCHEMA_PATH) as f:
        db_schema = json.load(f)
    logger.info('Database schema file has been loaded!')


def query_select(query, t=None):
    logger.info('Executing query...')
    logger.info('Query: "{}"'.format(query))
    if t:
        logger.info('Tuple: {}'.format(t))
    cursor = connection.cursor()
    cursor.execute(query, t)
    return cursor.fetchall()


def get_table_schema_from_name(table_name):
    return db_schema.get(table_name)  # may return None


def decorate_rows(rows, table_name):
    element = db_schema.get(table_name)
    if element:
        columns = element['column_list']
        return list(map(lambda r: dict(zip(columns, r)), rows))
    else:
        pass  # todo: error/exception


def query_select_on_word(table_name, word_column_list, word):

    query_string = "SELECT * FROM {} ".format(table_name)
    query_string += "WHERE "
    query_string += " OR ".join(["{}=%s".format(w_col) for w_col in word_column_list])

    tup = tuple([word] * len(word_column_list))

    rows = query_select(query_string, tup)

    return decorate_rows(rows, table_name)


def join_one_to_many(element, from_table_name, to_table_name):
    from_schema = get_table_schema_from_name(from_table_name)
    to_schema = get_table_schema_from_name(to_table_name)

    query_string = "SELECT "
    query_string += ", ".join(["Z.{}".format(col) for col in to_schema['column_list']])
    query_string += " "
    query_string += "FROM {} A, {} Z ".format(from_schema['table_name'], to_schema['table_name'])
    query_string += "WHERE "
    query_string += " AND ".join(["A.{}=Z.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(from_table_name, to_table_name)])
    query_string += " AND "
    query_string += " AND ".join(['A.{}=%s'.format(primary, element[primary])
                                 for primary in from_schema['primary_key_list']])

    tup = tuple([element[primary] for primary in from_schema['primary_key_list']])

    rows = query_select(query_string, tup)

    return decorate_rows(rows, to_table_name)


def join_many_to_many(element, from_table_name, to_table_name, by_table_name):
    from_schema = get_table_schema_from_name(from_table_name)
    to_schema = get_table_schema_from_name(to_table_name)
    by_schema = get_table_schema_from_name(by_table_name)

    query_string = "SELECT "
    # relation/by columns
    query_string += ", ".join(["Z.{}".format(col)
                               for col in to_schema['column_list']]
                              +
                              ["Y.{}".format(col)
                               for col in by_schema['column_list']])
    query_string += " "
    query_string += "FROM {} A, {} Y, {} Z ".format(from_table_name, by_table_name, to_table_name)
    query_string += "WHERE "
    query_string += " AND ".join(["A.{}=Y.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(from_table_name, by_table_name)])

    query_string += " AND "
    query_string += " AND ".join(["Y.{}=Z.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(by_table_name, to_table_name)])

    query_string += " AND "
    query_string += " AND ".join(['A.{}=%s'.format(primary, element[primary])
                                 for primary in from_schema['primary_key_list']])

    tup = tuple([element[primary] for primary in from_schema['primary_key_list']])

    rows = query_select(query_string, tup)

    first_type = decorate_rows(rows, to_table_name)
    index = len(first_type)
    second_type = decorate_rows([r[index:] for r in rows], by_table_name)

    return first_type, second_type


def get_paired_reference_key_list(from_table_name, to_table_name):
    from_schema = get_table_schema_from_name(from_table_name)
    to_schema = get_table_schema_from_name(to_table_name)
    from_references = from_schema['references']
    to_references = to_schema['references']
    if from_references:
        if from_references.get(to_table_name):
            return zip(from_references[to_table_name]['foreign_key_list'], from_references[to_table_name]['reference_key_list'])
    if to_references:
        if to_references.get(from_table_name):
            return zip(to_references[from_table_name]['foreign_key_list'], to_references[from_table_name]['reference_key_list'])
    return None
