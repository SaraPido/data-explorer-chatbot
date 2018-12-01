import logging

from server.core import database
from server.core import context
from server.core.actions import messages

logger = logging.getLogger(__name__)


# Helpers


def find_element_by_word(element_type, word):
    element_list = database.query_select_on_word(element_type, word)
    if element_list:
        context.add_element_to_context_list(element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_type, element_list[0])
        return element_list
    else:
        return None  # todo: error/exception


def get_element_type_and_value_list(element):
    # TODO: write doc and refactor name of the method
    element_type = element['type']
    value_list = element['value']
    if element_type.endswith('_list'):
        element_type = element_type[:-5]
    else:
        value_list = [value_list]
    return element_type, value_list


def get_element_attribute_list(element_type):
    """
    This method returns the list of attributes can be directly asked by the user,
    it removes the list of "word" since that parameter is always present.

    :param element_type: the string representing the type of the element
    :return: the list of string representing the attributes
    """
    el_properties = database.get_element_properties(element_type)
    attribute_list = [e for e in el_properties['column_list'] if
                      e not in el_properties['foreign_key_list'] and
                      e not in el_properties['word_list']]
    attribute_list.extend([e['type'] for e in el_properties['relation_list']])
    return attribute_list


#

#

# Actions

# todo: maybe all this way....
def action_find_element_by_word(element_type, word):
    logger.info('Executing "action_find_element_by_word"')
    message = None
    buttons = []

    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    if word:
        element_list = find_element_by_word(element_type, word)
        if not element_list:
            message = 'Nothing has been found with {} {}'.format(element_type, word)
        else:
            message = 'Here the results for {} {}:\n'.format(element_type, word)
            message += messages.get_message_word_list(element_type, element_list)
    else:
        message = "No word entity has been received..."
    return {'message': message, 'buttons': buttons}


# todo: maybe all this way....
def action_view_element_column_list():
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    logger.info('Executing "action_view_element_column_list"')
    message = None
    buttons = []

    element = context.get_last_element_from_context_list()
    buttons = []
    if element:
        message = 'Click the desired column:'
        type_, value_list = get_element_type_and_value_list(element)
        for e in get_element_attribute_list(type_):
            buttons.append({'title': e, 'payload': '/view_element_' + e})
    else:
        message = 'The context_list is empty!'
    return {'message': message, 'buttons': buttons}


def action_view_element_attribute(attribute):
    logger.info('Executing "action_view_element_attribute"')
    message = None
    buttons = []

    element = context.get_last_element_from_context_list()
    if element:
        type_, value_list = get_element_type_and_value_list(element)
        if attribute in get_element_attribute_list(type_):
            # todo: control if there is a join todo :D
            message = 'Results for attribute {}:\n'.format(attribute)
            message += messages.get_message_word_list_with_attribute(type_, value_list, attribute)
        else:
            message = 'The {} attribute is not part of {}\n'.format(attribute, type_)
            res = action_view_element_column_list()
            message += res.get('message')
            buttons = res.get('buttons')
    else:
        message = 'The context_list is empty!'
    return {'message': message, 'buttons': buttons}
