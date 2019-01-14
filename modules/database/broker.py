import json
import logging
import string

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


def execute_query_select(query, t=None):
    # TODO: in order to have a debug working quickly
    query += ' LIMIT 100'
    logger.info('Executing query...')
    logger.info('Query: "{}"'.format(query))
    if t:
        logger.info('Tuple: {}'.format(t))
    cursor = connection.cursor()
    cursor.execute(query, t)
    return cursor.fetchall()


def get_table_schema_from_name(table_name):
    return db_schema.get(table_name)  # may return None


def find_on_value(value_column_list, value, operator='=', *table_names):
    tables = get_tables_dict(table_names)

    query_string = "SELECT DISTINCT " + get_select_tables_query_string([tables[0]])
    query_string += " FROM " + get_from_tables_query_string(tables)
    query_string += " WHERE "
    where_tables_pair = get_where_tables_pair_query_string(tables)
    query_string += where_tables_pair + " AND " if where_tables_pair else ""
    query_string += get_where_on_value_query_string(tables[-1], value_column_list, operator)

    tup = tuple([value] * len(value_column_list))
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, tables)


def join_from_element(element, *table_names):
    tables = get_tables_dict(table_names)

    query_string = "SELECT " + get_select_tables_query_string(tables[::-1][:-1])
    query_string += " FROM " + get_from_tables_query_string(tables)
    query_string += " WHERE "
    where_tables_pair = get_where_tables_pair_query_string(tables)
    query_string += where_tables_pair + " AND " if where_tables_pair else ""
    query_string += get_where_on_primary_query_string(tables[0], element)

    tup = tuple([element[primary] for primary in tables[0]['schema']['primary_key_list']])
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, tables[::-1])


def get_dictionary_result(q_string, q_tuple, rows, tables):

    query = {'q_string': q_string, 'q_tuple': q_tuple}

    to_columns = tables[0]['schema']['column_list']
    value = list(map(lambda r: dict(zip(to_columns, r)), rows))

    index = len(to_columns)
    by_value = []

    # if there is a "by element"
    if len(tables) > 2:
        by_columns = tables[1]['schema']['column_list']
        by_value = list(map(lambda r: dict(zip(by_columns, r[index:])), rows))

    return {'query': query, 'value': value, 'by_value': by_value, 'real_value_length': len(value)}


# query helper

def get_tables_dict(table_names):
    tables = []
    num2alpha = dict(zip(range(1, 27), string.ascii_lowercase))
    for i, tn in enumerate(table_names):
        tables.append({"table_name": tn, "schema": get_table_schema_from_name(tn), "letter": num2alpha[i + 1]})
    return tables


# query creators

def get_select_tables_query_string(tables):
    col_string_list = []
    for t in tables:
        col_string_list.extend("{}.{}".format(t['letter'], col) for col in t['schema']['column_list'])
    return ", ".join(col_string_list)


def get_from_tables_query_string(tables):
    tab_string_list = []
    for t in tables:
        tab_string_list.append("{} {}".format(t['table_name'], t['letter']))
    return ", ".join(tab_string_list)


def get_where_tables_pair_query_string(tables):
    pair_string_list = []
    for i, t in enumerate(tables):
        if i < len(tables) - 1:
            pair_string_list.extend(["{}.{}={}.{}".format(t['letter'], p[0], tables[i+1]['letter'], p[1])
                                     for p in
                                     get_paired_reference_key_list(t, tables[i+1])])
    return " AND ".join(pair_string_list)


def get_where_on_value_query_string(single_table, value_column_list, operator):
    return " OR ".join(["{}.{} {} %s".format(single_table['letter'], v_col, operator) for v_col in value_column_list])


def get_where_on_primary_query_string(single_table, element):
    return " AND ".join(['{}.{}=%s'.format(single_table['letter'], primary, element[primary])
                         for primary in single_table['schema']['primary_key_list']])


def get_paired_reference_key_list(from_table, to_table):
    from_table_name = from_table['table_name']
    to_table_name = to_table['table_name']
    from_schema = from_table['schema']
    to_schema = to_table['schema']
    from_references = from_schema['references']
    to_references = to_schema['references']
    if from_references:
        if from_references.get(to_table_name):
            return zip(from_references[to_table_name]['foreign_key_list'], from_references[to_table_name]['reference_key_list'])
    if to_references:
        if to_references.get(from_table_name):
            return zip(to_references[from_table_name]['reference_key_list'], to_references[from_table_name]['foreign_key_list'])
    return None
