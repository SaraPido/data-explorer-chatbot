import logging
import json

from modules.database import broker
from modules.settings import DB_CONCEPT_PATH

logger = logging.getLogger(__name__)

db_concept = []

# Database properties


def load_db_concept():
    global db_concept
    logger.info('Database concept file:\n'
                '"' + DB_CONCEPT_PATH + '"')
    logger.info('Loading database concept file...')
    with open(DB_CONCEPT_PATH) as f:
        db_concept = json.load(f)
    logger.info('Database concept file has been loaded!')


def get_all_element_names():
    return [e.get('element_name') for e in db_concept]


def get_element(element_name):
    for e in db_concept:
        if e.get('element_name') == element_name:
            return e
    return None


def extract_show_columns(element_name):
    e = get_element(element_name)
    return e.get('show_columns') if e else None


def extract_relations(element_name):
    e = get_element(element_name)
    return e.get('relations') if e else None


def extract_all_attributes(element_name):
    e = get_element(element_name)
    return e.get('attributes') if e else None


def extract_attributes_with_keyword(element_name):
    attributes = extract_all_attributes(element_name)
    if attributes:
        return [a for a in attributes if a.get('keyword')]
    return None


def get_attribute_by_name(element_name, attribute_name):
    attributes = extract_attributes_with_keyword(element_name)
    for a in attributes:
        if a.get('keyword') == attribute_name:
            return a
    return None


def get_attribute_without_keyword_by_type(element_name, attribute_type):
    attributes = [a for a in extract_all_attributes(element_name)
                  if a not in extract_attributes_with_keyword(element_name)]
    for a in attributes:
        if a.get('type') == attribute_type:
            return a
    return None


def query_find(element_name, attributes):
    e = get_element(element_name)
    table_name = e.get('table_name')
    # todo: operator should be put in the executor phase, now in broker there is the control
    result_element = broker.query_find(table_name, attributes)
    result_element['element_name'] = element_name
    return result_element


def query_join(element, relation_name):
    all_relations = extract_relations(element['element_name'])

    # there should always be the relation we want, the control is made in the executor
    relation = [rel for rel in all_relations if rel['keyword'] == relation_name][0]

    result_element = broker.query_join(element, relation)
    result_element['element_name'] = relation['element_name']
    return result_element

"""

def query_select_on_word(element_name, word, operator):
    el_properties = db_concept[element_name]
    table_name = el_properties['table_name']
    word_column_list = el_properties['word_column_list']
    result_element = broker.find_on_value(word_column_list, word, operator, table_name)
    result_element['element_name'] = element_name
    return result_element


def query_select_on_number(element_name, number, operator):
    el_properties = db_concept[element_name]
    table_name = el_properties['table_name']
    number_column_list = el_properties['number_column_list']
    result_element = broker.find_on_value(number_column_list, number, operator, table_name)
    result_element['element_name'] = element_name
    return result_element


def query_select_on_related_element_word(element_name, related_element_name, word, operator):
    el_properties = db_concept[element_name]
    related_el_properties = db_concept[related_element_name]
    table_name = el_properties['table_name']
    related_table_name = related_el_properties['table_name']
    related_word_column_list = related_el_properties['word_column_list']
    by_table_name = extract_by_table_name_if_necessary(element_name, related_element_name)
    result_element = broker.find_on_value(related_word_column_list, word, operator,
                                          table_name, by_table_name, related_table_name)
    result_element['element_name'] = element_name
    return result_element


def query_select_on_related_element_number(element_name, related_element_name, number, operator):
    el_properties = db_concept[element_name]
    related_el_properties = db_concept[related_element_name]
    table_name = el_properties['table_name']
    related_table_name = related_el_properties['table_name']
    related_number_column_list = related_el_properties['number_column_list']
    by_table_name = extract_by_table_name_if_necessary(element_name, related_element_name)
    result_element = broker.find_on_value(related_number_column_list, number, operator,
                                          table_name, by_table_name, related_table_name)
    result_element['element_name'] = element_name
    return result_element


def query_join_with_related_element(element, related_element_name, by_element_name=None):
    from_table_name = db_concept[element['element_name']]['table_name']
    to_table_name = db_concept[related_element_name]['table_name']
    by_table_name = extract_by_table_name_if_necessary(element['element_name'], related_element_name, by_element_name)
    # element['value'][0] because we are joining starting from 1 value
    if by_table_name:
        result_element = broker.join_from_element(element['value'][0], from_table_name, by_table_name, to_table_name)
    else:
        result_element = broker.join_from_element(element['value'][0], from_table_name, to_table_name)
    result_element['element_name'] = related_element_name
    return result_element


def extract_by_table_name_if_necessary(element_name, related_element_name, by_element_name=None):
    if not by_element_name:
        # if the relations is complex, i.e. multi elements
        complex_relation = db_concept[element_name]['relations'][related_element_name]
        if complex_relation:
            # taking the first because I know is the only one
            by_element_name = complex_relation[0]
    return db_concept[by_element_name]['table_name'] if by_element_name else None
"""


"""


def are_elements_related(element_name, related_element_name, by_element_name=None):
    element_properties = get_element_properties(element_name)
    related = related_element_name in element_properties['relations'].keys()
    if related:
        complex_relation = element_properties['relations'][related_element_name]
        # if there they are NOT directly related or there is only one way to reach each other
        if not complex_relation or len(complex_relation) == 1:
            return True
        # if there are multiple ways, check by_element_name
        return by_element_name in complex_relation


def is_element_findable_by_word(element_name, directly=False):
    el_concept = db_concept.get(element_name)
    # it can be found by name only if it is of type primary or if secondary but in a join
    if el_concept.get('word_column_list'):
        if directly:
            return el_concept.get('type') == 'primary'
        else:
            return el_concept.get('type') == 'primary' or el_concept.get('type') == 'secondary'


def is_element_findable_by_number(element_name, directly=False):
    el_concept = db_concept.get(element_name)
    # it can be found by name only if it is of type primary or if secondary but in a join
    if el_concept.get('number_column_list'):
        return directly and el_concept.get('type') == 'primary' or el_concept.get('type') == 'secondary'

"""
