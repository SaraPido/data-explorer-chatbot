import logging
import json

from modules.database import broker
from modules.settings import DB_CONCEPT_PATH

logger = logging.getLogger(__name__)

db_concept = None


def query_select_on_word(element_name, word):
    el_properties = db_concept[element_name]
    table_name = el_properties['table_name']
    word_column_list = el_properties['word_column_list']
    res = broker.query_select_on_word(table_name, word_column_list, word)
    return res


def query_simple_join_with_related_element(element_name, element_value, related_element_name):
    from_table_name = db_concept[element_name]['table_name']
    to_table_name = db_concept[related_element_name]['table_name']
    res = broker.join_one_to_many(element_value, from_table_name, to_table_name)
    return res


def query_double_join_with_related_element(element_name, element_value, related_element_name, by_element_name):
    from_table_name = db_concept[element_name]['table_name']
    to_table_name = db_concept[related_element_name]['table_name']
    by_table_name = db_concept[by_element_name]['table_name']
    res = broker.join_many_to_many(element_value, from_table_name, to_table_name, by_table_name)
    return res


# Database properties

def load_db_concept():
    global db_concept
    logger.info('Database concept file:\n'
                '"' + DB_CONCEPT_PATH + '"')
    logger.info('Loading database concept file...')
    with open(DB_CONCEPT_PATH) as f:
        db_concept = json.load(f)
    logger.info('Database concept file has been loaded!')


def get_element_properties(element_name):
    return db_concept.get(element_name)  # may return None


def get_all_element_names():
    return list(db_concept.keys())


def is_element_findable_by_word(element_name):
    return element_name in (k for k, v in db_concept.items() if v['word_column_list'])
