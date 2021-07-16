import logging
import json

from modules.database import broker
from settings import DB_CONCEPT_PATH

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


def get_all_primary_element_names():
    res = []
    for e in db_concept:
        if e.get('type') == 'primary':
            res.append(e.get('element_name'))
    return res


def get_all_primary_element_names_and_aliases():
    res = []
    for e in db_concept:
        if e.get('type') == 'primary':
            res.extend([e.get('element_name')] + e.get('aliases', []))
    return res


def get_element_aliases(element_name):
    element = extract_element(element_name)
    return element.get('aliases', [])


def get_element_name_from_possible_alias(element_or_alias_name):
    for e in db_concept:
        if e.get('element_name') == element_or_alias_name or element_or_alias_name in e.get('aliases', []):
            return e.get('element_name')
    return None


def extract_element(element_name):
    for e in db_concept:
        if e.get('element_name') == element_name:
            return e
    return None


def extract_show_columns(element_name):
    print('extract_show_columns ', element_name)
    if type(element_name)==dict:
        e = extract_element(element_name['element_name'])
    else:
        e = extract_element(element_name)

    print('e ', e)
    return e.get('show_columns') if e else None


def extract_relations(element_name):
    e = extract_element(element_name)
    return e.get('relations') if e else None


def extract_all_attributes(element_name):
    e = extract_element(element_name)
    return e.get('attributes') if e else None


def extract_attributes_with_keyword(element_name):
    attributes = extract_all_attributes(element_name)
    if attributes:
        return [a for a in attributes if a.get('keyword')]
    return None


def get_attribute_by_name(element_name, attribute_name):
    attributes = extract_attributes_with_keyword(element_name)
    return next((a for a in attributes if a.get('name')==attribute_name), None)


def get_attribute_without_keyword_by_type(element_name, attribute_type):
    attributes = [a for a in extract_all_attributes(element_name)
                  if a not in extract_attributes_with_keyword(element_name)]
    for a in attributes:
        if a.get('type') == attribute_type:
            return a
    return None


def get_element_show_string(element_name, element_value):
    print('\nget_element_show_string ', element_name, element_value)
    show_columns = extract_show_columns(element_name)
    print('show_columns ', show_columns)
    print('element value ', element_value)
    print(', '.join((sh['keyword'] + ': ' if sh.get('keyword') else '') + ' '.join(str(element_value[x]) for x in sh['columns']) for sh in show_columns))
    return ', '.join((sh['keyword'] + ': ' if sh.get('keyword') else '')
                     + ' '.join(str(element_value[x]) for x in sh['columns'])
                     for sh in show_columns)


def query_find(element_name, attributes):
    print('query_find', element_name, attributes)
    e = extract_element(element_name)
    table_name = e.get('table_name')
    print('table_name', table_name)
    result_element = broker.query_find(table_name, attributes)
    result_element['element_name'] = element_name
    print('result_element', result_element)
    return result_element


def query_join(element, relation_name):
    all_relations = extract_relations(element['element_name'])

    # there should always be the relation we want, the control is made in the executor
    relation = [rel for rel in all_relations if rel['keyword'] == relation_name][0]

    result_element = broker.query_join(element, relation)
    result_element['element_name'] = relation['element_name']
    return result_element


def simulate_view(element_name):
    print('\nsimulate_view resolver')
    e = extract_element(element_name)
    print('e ', e)
    table_name = e.get('table_name')
    print('table name ', table_name)
    result_element = broker.simulate_view(table_name)
    print('result_element', result_element)
    return result_element