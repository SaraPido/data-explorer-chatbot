import logging
import mysql.connector
import json

logger = logging.getLogger(__name__)

connection = None
db_properties = None


# Queries

def query_select(query, t=None):
    logger.info('Executing query...')
    logger.info('Query: "{}"'.format(query))
    if t:
        logger.info('Tuple: {}'.format(t))
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


def query_select_join_on_attribute(element_type, element_value, attribute):
    from_el_properties = get_element_properties(element_type)
    relation = next(iter([e for e in from_el_properties['relation_list'] if e['type'] == attribute]))
    to_el_properties = get_element_properties(attribute)
    #if relation['by'] is '':
    query_string = get_query_string_join_one_to_many(element_value, relation,
                                                     from_el_properties, to_el_properties)
    #else:
        #by_el_properties = get_element_properties(relation['by'])
        #query_string = get_query_string_join_many_to_many(element_value, relation,
                                                         # from_el_properties, by_el_properties, to_el_properties)
    rows = query_select(query_string)
    return decorate_rows(to_el_properties['type'], rows)


def get_query_string_join_one_to_many(element_value, relation, from_el_properties, to_el_properties):
    query_string = "SELECT "
    query_string += ", ".join(["B.{}".format(name) for name in to_el_properties['column_list']])
    query_string += " FROM {} A, {} B ".format(from_el_properties['table_name'],
                                               to_el_properties['table_name'])
    query_string += "WHERE "
    query_string += "A.{}=B.{} ".format(relation['from'], relation['to'])
    query_string += "and A.{}={}".format(from_el_properties['id'], element_value[from_el_properties['id']])
    return query_string


def get_query_string_join_many_to_many(element_value, relation, from_el_properties, by_el_properties, to_el_properties):
    query_string = "SELECT "
    query_string += ", ".join(["C.{}".format(name) for name in to_el_properties['column_list']])
    query_string += " FROM {} A, {} B, {} C".format(from_el_properties['table_name'],
                                                    by_el_properties['table'],
                                                    to_el_properties['table_name'])
    return query_string


def decorate_rows(element_type, rows):
    element = next(filter(lambda el: el['type'] == element_type, db_properties), None)
    if element:
        columns = element['column_list']
        return list(map(lambda r: dict(zip(columns, r)), rows))
    else:
        pass # todo: error/exception


# Database properties

# todo: hybrid now
def load_db_properties(db_concept_path):
    global db_properties
    logger.info('Loading database properties...')
    with open(db_concept_path) as f:
        db_properties = json.load(f)
    logger.info('Database concept file has been loaded!')
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
