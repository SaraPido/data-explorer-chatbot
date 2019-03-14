import copy
import json
import logging
import os
import string

from pprint import pprint
from mysql import connector

from settings import DATABASE_NAME, DB_SCHEMA_PATH, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, QUERY_LIMIT

logger = logging.getLogger(__name__)

db_schema = None


def test_connection():
    logger.info('Database:\n'
                '"' + DATABASE_NAME + '"')
    logger.info('Testing connection with the database...')
    connection = connect()
    logger.info('Connection succeeded! Closing connection...')
    disconnect(connection)
    logger.info('Connection closed.')


def connect():
    return connector.connect(user=DATABASE_USER,
                             password=DATABASE_PASSWORD,
                             host=DATABASE_HOST,
                             database=DATABASE_NAME)


def disconnect(connection):
    connection.close()


def load_db_schema():
    global db_schema
    logger.info('Database schema file:\n'
                '"' + DB_SCHEMA_PATH + '"')
    logger.info('Loading database schema file...')
    with open(DB_SCHEMA_PATH) as f:
        db_schema = json.load(f)
    logger.info('Database schema file has been loaded!')


def execute_query_select(query, t=None):
    # HERE FORCING THE LIMIT OF THE QUERY
    if QUERY_LIMIT:
        query += ' LIMIT 100'
    logger.info('Executing query...')
    logger.info('Query: "{}"'.format(query))
    if t:
        logger.info('Tuple: {}'.format(t))

    connection = connect()
    cursor = connection.cursor()
    cursor.execute(query, t)
    rows = cursor.fetchall()
    cursor.close()
    disconnect(connection)
    return rows


def get_dictionary_result(q_string, q_tuple, rows, columns, attributes):
    query = {'q_string': q_string, 'q_tuple': q_tuple}

    value = list(map(lambda r: dict(zip(columns, r)), rows))

    return {'query': query,
            'value': value,
            'real_value_length': len(value),
            'attributes': attributes}


def get_table_schema_from_name(table_name):
    return db_schema.get(table_name)  # may return None


def query_find(in_table_name, attributes):

    columns = get_table_schema_from_name(in_table_name)['column_list']  # the schema has "list"

    label_attributes(attributes)

    for a in attributes:
        if not a.get('operator'):
            a['operator'] = '='

    query_string = "SELECT DISTINCT " + get_SELECT_query_string(columns)  # ugly but correct
    query_string += " FROM " + get_FROM_query_string(attributes, in_table_name)
    query_string += " WHERE "
    where_join_string = get_WHERE_JOIN_query_string(attributes)
    query_string += where_join_string + " AND " if where_join_string else ""
    query_string += get_WHERE_ATTRIBUTES_query_string(attributes)

    pprint(attributes)
    pprint(query_string)

    values = []
    for a in attributes:
        # if 'a' is a REAL conversational attribute
        if a.get('value'):
            val = str(a['value'])
            if a['operator'] == 'LIKE':
                val = '%'+val+'%'
            values.extend([val] * len(a['columns']))
        # if 'a' is a mocked relation
        elif a.get('join_values'):
            values.extend(a['join_values'])
    tup = tuple(values)
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, columns, attributes)


def query_join(element, relation):

    to_table_name = relation['by'][-1]['to_table_name']  # the table is the last one of the last "by" in the relation

    to_schema = get_table_schema_from_name(to_table_name)
    to_columns = to_schema['column_list']  # the schema has "list"

    from_table_name = relation['by'][0]['from_table_name']  # the table is the one of the first "by" in the relation

    from_schema = get_table_schema_from_name(from_table_name)
    primary_columns = from_schema['primary_key_list']
    relation['join_values'] = [element['value'][0][x] for x in primary_columns]

    relation['operator'] = '='

    relation['columns'] = primary_columns

    relation = get_reverse_relation(copy.deepcopy(relation))  # HERE I REVERT THE RELATION to standardize with the attributes

    label_attributes([relation])

    query_string = "SELECT DISTINCT " + get_SELECT_query_string(to_columns)
    query_string += " FROM " + get_FROM_query_string([relation])
    query_string += " WHERE " + get_WHERE_JOIN_query_string([relation])
    query_string += " AND " + get_WHERE_ATTRIBUTES_query_string([relation])

    tup = tuple(relation['join_values'])
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, to_columns, [relation])  # mocking the relation as attribute


def get_reverse_relation(relation):
    if relation.get('by'):
        relation['by'].reverse()  # reverting the list like a boss
        # here I swap like a boss
        for r in relation['by']:
            r['to_table_name'], r['from_table_name'] = r['from_table_name'], r['to_table_name']
            r['to_columns'], r['from_columns'] = r['from_columns'], r['to_columns']
    return relation


# query helper

def label_attributes(attributes):
    num2alpha = dict(zip(range(1, 27), string.ascii_lowercase))
    i = 2  # the 'a' is taken by the first
    for a in attributes:
        if a.get('by'):
            for idx, rel in enumerate(a['by']):
                if not idx:
                    rel['from_letter'] = 'a'
                    rel['to_letter'] = num2alpha[i]
                else:
                    rel['from_letter'] = num2alpha[i]
                    rel['to_letter'] = num2alpha[i + 1]
                    i += 1
            a['letter'] = a['by'][-1]['to_letter']  # the last letter
            i += 1
        else:
            a['letter'] = 'a'


# query creators

def get_SELECT_query_string(columns):
    col_string_list = []
    for col in columns:
        col_string_list.append("a.{}".format(col))
    return ", ".join(col_string_list)


def get_FROM_query_string(attributes, table_name=None):
    tab_string_list = []
    if table_name:
        tab_string_list.append('{} a'.format(table_name))
    for a in attributes:
        for rel in a.get('by', []):
            from_tab_string = '{} {}'.format(rel['from_table_name'], rel['from_letter'])
            if from_tab_string not in tab_string_list:
                tab_string_list.append(from_tab_string)
            to_tab_string = '{} {}'.format(rel['to_table_name'], rel['to_letter'])
            if to_tab_string not in tab_string_list:
                tab_string_list.append(to_tab_string)
    return ", ".join(tab_string_list)


def get_WHERE_JOIN_query_string(attributes):
    join_string_list = []
    for a in attributes:
        for rel in a.get('by', []):
            # the lists must be equally long, obviously
            for i in range(len(rel['from_columns'])):
                join_string_list.append('{}.{}={}.{}'.format(rel['from_letter'],
                                                             rel['from_columns'][i],
                                                             rel['to_letter'],
                                                             rel['to_columns'][i]))
    return " AND ".join(join_string_list)


def get_WHERE_ATTRIBUTES_query_string(attributes):
    attr_string_list = []
    for a in attributes:
        attr = "( "

        attr += " OR ".join(["{}.{} {} %s".format(a['letter'],  # not so pretty
                                                  col,
                                                  a['operator'])
                             for col in a['columns']])
        attr += " )"
        attr_string_list.append(attr)
    return " AND ".join(attr_string_list)
