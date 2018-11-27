import logging
import json

from server.core import database
from server.core import context

logger = logging.getLogger(__name__)


db_properties = None


def load_db_properties(db_properties_path):
    global db_properties
    logger.info('Loading database properties...')
    with open(db_properties_path) as f:
        db_properties = json.load(f)
    logger.info('Database properties have been loaded!')
    #logger.info(pformat(db_properties))


''' HELPERS '''


def get_element_column_list(element_type):
    element = next(filter(lambda el: el['type'] == element_type, db_properties), None)
    return element['column_list']


def get_element_word_list(element_type):
    element = next(filter(lambda el: el['type'] == element_type, db_properties), None)
    return element['word_list']


def select_on_word(element_type, word):
    query_string = "SELECT * FROM " + element_type.capitalize() + " "
    column_list = get_element_word_list(element_type)
    # TODO: Review this part...
    # e.g. "SELECT * FROM Teacher WHERE name='"+word+"' OR surname='"+word+"'"
    for i, col in enumerate(column_list):
        if i == 0:
            query_string += "WHERE "
        query_string += "" + col + "='" + word + "'"
        # if not the last column
        if i != len(column_list) - 1:
            query_string += " OR "
    res = database.query_select(query_string)
    if len(res) > 0:
        return res
    else:
        return None


def decorate_rows(element_type, rows):
    element = next(filter(lambda el: el['type'] == element_type, db_properties), None)
    if element:
        columns = element['column_list']
        return list(map(lambda r: dict(zip(columns, r)), rows))


def find_element_by_word(element_type, word):
    rows = select_on_word(element_type, word)
    if rows:
        element_list = decorate_rows(element_type, rows)
        context.add_element_to_context_list(element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_type, element_list[0])
        return element_list
    else:
        return None


def get_message_word_list(element_type, element_list):
    message = 'Results:\n'
    word_list = get_element_word_list(element_type)
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in word_list)
        if i == len(e) - 1: message += '\n'
    return message


def get_message_word_list_and_attribute_list(element_type, element_list, attribute_type):
    message = 'Results for {' + attribute_type + '}:\n'
    words_list = get_element_word_list(element_type)
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in words_list)
        message += ': ' + str(e[attribute_type])
        if i == len(e) - 1: message += '\n'
    return message


''' ACTIONS '''


def run_action_find_element_by_word(self, dispatcher, tracker, domain, element_type):
    word = next(tracker.get_latest_entity_values('word'), None)
    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    if word:
        element_list = find_element_by_word(element_type, word)
        if not element_list:
            message = 'Nothing has been found with: ' + word
        else:
            message = get_message_word_list(element_type, element_list)
    else:
        message = "No words entity has been received..."
    dispatcher.utter_message(message)

    return []


def run_action_view_element_id(self, dispatcher, tracker, domain, attribute_type):
    element = context.get_last_element_from_context_list()
    if not element:
        type = element['type']
        value_list = element['value']
        if type.endswith('_list'):
            type = type[:-5]
        else:
            value_list = [value_list]
        if attribute_type in get_element_column_list(type):
            message = get_message_word_list_and_attribute_list(type, value_list, attribute_type)
        else:
            message = 'The specified attribute is not part of ' + type
    else:
        message = 'Problems with the context list here...'
    dispatcher.utter_message(message)
    return []
