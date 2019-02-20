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


def get_dictionary_result(q_string, q_tuple, rows, columns):
    query = {'q_string': q_string, 'q_tuple': q_tuple}

    value = list(map(lambda r: dict(zip(columns, r)), rows))

    # if there is a "by element"
    # todo: consider the case  of "by_value".. -> what if I want to select more?

    return {'query': query, 'value': value, 'by_value': [], 'real_value_length': len(value)}


def get_table_schema_from_name(table_name):
    return db_schema.get(table_name)  # may return None


def query_find(in_table_name, attributes):

    columns = get_table_schema_from_name(in_table_name)['column_list']  # the schema has "list"

    label_attributes(attributes)

    for a in attributes:
        if not a.get('operator'):
            a['operator'] = '='

    query_string = "SELECT DISTINCT " + get_SELECT_query_string(columns, 'a')  # ugly but correct
    query_string += " FROM " + get_FROM_query_string(attributes, in_table_name)
    query_string += " WHERE "
    where_join_string = get_WHERE_JOIN_query_string(attributes)
    query_string += where_join_string + " AND " if where_join_string else ""
    query_string += get_WHERE_ATTRIBUTES_query_string(attributes)

    values = []
    for a in attributes:
        # TODO AAA review this part: using "LIKE" for words
        if a['type'] == 'word':
            a['value'] = '%'+a['value']+'%'
        values.extend([a['value']] * len(a['columns']))
    tup = tuple(values)
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, columns)


def query_join(element, relation):

    to_table_name = relation['by'][-1]['to_table_name']  # the table is the last one of the last "by" in the relation

    to_schema = get_table_schema_from_name(to_table_name)
    to_columns = to_schema['column_list']  # the schema has "list"

    from_table_name = relation['by'][0]['from_table_name']  # the table is the one of the first "by" in the relation

    from_schema = get_table_schema_from_name(from_table_name)
    primary_columns = from_schema['primary_key_list']
    primary_values = [element['value'][0][x] for x in primary_columns]

    relation['operator'] = '='

    relation['columns'] = primary_columns

    label_attributes([relation])

    query_string = "SELECT DISTINCT " + get_SELECT_query_string(to_columns, relation['letter'])
    query_string += " FROM " + get_FROM_query_string([relation])
    query_string += " WHERE " + get_WHERE_JOIN_query_string([relation])
    query_string += " AND " + get_WHERE_ATTRIBUTES_query_string([relation], join=True)

    tup = tuple(primary_values)
    rows = execute_query_select(query_string, tup)
    return get_dictionary_result(query_string, tup, rows, to_columns)


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

def get_SELECT_query_string(columns, letter):
    # todo: what if I want to select more?
    col_string_list = []
    for col in columns:
        col_string_list.append("{}.{}".format(letter, col))
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


def get_WHERE_ATTRIBUTES_query_string(attributes, join=False):
    attr_string_list = []
    for a in attributes:
        attr = "( "

        # TODO AAA review this part: using "LIKE" for words
        if a['type'] == 'word':
            a['operator'] = 'LIKE'

        attr += " OR ".join(["{}.{} {} %s".format(a['letter'] if not join else 'a', # not so pretty
                                                  col,
                                                  a['operator'])
                             for col in a['columns']])
        attr += " )"
        attr_string_list.append(attr)
    return " AND ".join(attr_string_list)

