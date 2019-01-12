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
    result_element = broker.query_select_on_word(table_name, word_column_list, word)
    result_element['element_name'] = element_name
    return result_element


def query_join_with_related_element(element, related_element_name, by_element_name=None):
    from_table_name = db_concept[element['element_name']]['table_name']
    to_table_name = db_concept[related_element_name]['table_name']
    by_table_name = db_concept[by_element_name]['table_name'] if by_element_name else None
    # element['value'][0] because we are joining starting from 1 value
    result_element = broker.query_join(element['value'][0], from_table_name, to_table_name, by_table_name)
    result_element['element_name'] = related_element_name
    return result_element


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
    return element_name in (k for k, v in db_concept.items() if v.get('word_column_list'))
