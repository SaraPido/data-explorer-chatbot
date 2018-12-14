import logging
import json

from nested_lookup import nested_lookup

from modules.database import broker

logger = logging.getLogger(__name__)

db_concept = None


def query_select_on_word(element_type, word):
    el_properties = get_element_properties(element_type)
    table_name = el_properties['table_name']
    word_column_list = el_properties['word_column_list']
    res = broker.query_select_on_word(table_name, word_column_list, word)
    return res


def query_simple_join_with_related_element(element_type, element_value, related_element_type):
    el_properties = get_element_properties(element_type)
    from_table_name = el_properties['table_name']
    to_table_name = get_element_properties(related_element_type)['table_name']
    res = broker.join_one_to_many(element_value, from_table_name, to_table_name)
    return res


def query_double_join_with_related_element(element_type, element_value, related_element_type,
                                           by_element_type):
    el_properties = get_element_properties(element_type)
    from_table_name = el_properties['table_name']
    to_table_name = get_element_properties(related_element_type)['table_name']
    rel = next(iter(r for r in el_properties['relation_list'] if r['type'] == related_element_type))
    by_table_name = next(iter(r['table_name'] for r in rel['by'] if r['type'] == by_element_type))
    res = broker.join_many_to_many(element_value, from_table_name, to_table_name, by_table_name)
    return res


# Database properties

def load_db_concept(db_concept_path):
    global db_concept
    logger.info('Loading database concept file...')
    with open(db_concept_path) as f:
        db_concept = json.load(f)
    logger.info('Database concept file has been loaded!')


def get_element_properties(element_type):
    for el in db_concept:
        if el['type'] == element_type:
            return el
    return None


def get_all_element_types():
    """
    It also finds the type of elements in many-to-many relations
    :return: the list of elements, with no repetitions
    """
    res = nested_lookup('type', db_concept)
    return list(set(res))


def is_element_type_findable_by_word(element_type):
    return element_type in (el['type'] for el in db_concept if el['word_column_list'])
