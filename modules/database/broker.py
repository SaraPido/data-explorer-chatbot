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


def query_find(table_name, attributes):

    columns = get_table_schema_from_name(table_name)['column_list'] # the schema has "list"

    label_attributes(attributes)

    query_string = "SELECT DISTINCT " + get_SELECT_query_string(columns)
    query_string += " FROM " + get_FROM_query_string(table_name, attributes)
    query_string += " WHERE "
    where_join_string = get_WHERE_JOIN_query_string(attributes)
    query_string += where_join_string + " AND " if where_join_string else ""
    query_string += get_WHERE_ATTRIBUTES_query_string(attributes)

    values = []
    for a in attributes:
        values.extend([a['value']] * len(a['columns']))
    tup = tuple(values)
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, columns)


def get_dictionary_result(q_string, q_tuple, rows, columns):
    query = {'q_string': q_string, 'q_tuple': q_tuple}

    value = list(map(lambda r: dict(zip(columns, r)), rows))

    # if there is a "by element"
    # todo: consider the case  of "by_value".. -> what if I want to select more?

    return {'query': query, 'value': value, 'by_value': [], 'real_value_length': len(value)}


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
    # todo: what if I want to select more?
    col_string_list = []
    for col in columns:
        col_string_list.append("a.{}".format(col))
    return ", ".join(col_string_list)


def get_FROM_query_string(table_name, attributes):
    tab_string_list = ['{} a'.format(table_name)]
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
        attr += " OR ".join(["{}.{} {} %s".format(a['letter'],
                                                  col,
                                                  a['operator'])
                             for col in a['columns']])
        attr += " )"
        attr_string_list.append(attr)
    return " AND ".join(attr_string_list)


"""

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

"""


"""
for a in attributes:
    # todo review for self-relations...
    join_tables = []
    if a.get('table_name') != table_name:
        join_tables.extend([t for t in tables if t['table_name'] == table_name])
        if a.get('by_table_names'):
            join_tables.extend([t for t in tables if t['table_name'] in a['by_table_names']])
        join_tables.extend([t for t in tables if t['table_name'] == a['table_name']])
    for i, t in enumerate(join_tables):
        if i < len(join_tables) - 1:
            pair_string_list.extend(["{}.{}={}.{}".format(t['letter'], p[0], join_tables[i+1]['letter'], p[1])
                                     for p in
                                     get_paired_reference_key_list(t, join_tables[i+1])])
return " AND ".join(pair_string_list)
"""


"""

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
"""
