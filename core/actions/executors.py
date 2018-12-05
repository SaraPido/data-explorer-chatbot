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


def join_element_on_attribute(element, attribute):
    element_list = database.query_select_join_on_attribute(element['type'], element['value'], attribute)
    if element_list:
        context.add_element_to_context_list(attribute + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(attribute, element_list[0])
        return element_list
    else:
        return None  # todo: error/exception


#


def get_element_type_and_value_list(element):
    # TODO: write doc and refactor name of the method
    element_type = element['type']
    value_list = element['value']
    if element_type.endswith('_list'):
        element_type = element_type[:-5]
    else:
        value_list = [value_list]
    return element_type, value_list


#

def extract_element_id_column(element_properties):
    return next(col for col in element_properties['column_list'] if col == element_properties['id'])


def extract_element_attribute_list(element_properties):
    """
    This method returns the list of attributes can be directly asked by the user,
    it removes the list of "word" since that parameter is always present.

    :param element_properties: the db_properties of the element
    :return: the list of string representing the attributes
    """
    attribute_list = [e for e in element_properties['column_list'] if
                      e not in element_properties['foreign_key_list'] and
                      e not in element_properties['word_list']]
    attribute_list.extend(extract_element_relation_attribute_list(element_properties))
    return attribute_list


def extract_element_relation_attribute_list(element_properties):
    return [e['type'] for e in element_properties['relation_list']]


#

#

# Actions


def action_find_element_by_word(element_type, word, msg=''):
    logger.info('Executing "action_find_element_by_word"')
    message = msg
    buttons = []

    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    if word:
        element_list = find_element_by_word(element_type, word)
        if not element_list:
            message += 'NO RESULTS for element "{}" and word "{}"'.format(element_type, word)
        elif len(element_list) == 1:
            return action_view_element_info()
        else:
            message += 'SELECT:\n'
            buttons = messages.get_buttons_select_element(element_type, element_list)
    else:
        message = "No word entity has been received..."
    return {'message': message, 'buttons': buttons}


def action_select_element_by_position(position: int, msg=''):
    """

    :param position: position 1 is for element at index 0
    :param msg:
    :return:
    """
    logger.info('Executing "action_select_element_by_position"')
    element = context.get_last_element_from_context_list()
    message = msg
    buttons = []
    if element:
        type_, value_list = get_element_type_and_value_list(element)
        if len(value_list) == 1:
            message += 'THERE IS ONLY ONE ELEMENT\n'
            action_view_element_info(message)
        else:
            if position <= len(value_list):
                context.add_element_to_context_list(type_, value_list[position - 1])
                return action_view_element_info()
            else:
                message += 'THE SELECTION IS OUT OF RANGE'
    return {'message': message, 'buttons': buttons}


def action_view_element_relation_list(msg=''):
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    logger.info('Executing "action_view_element_relation_list"')
    message = msg
    buttons = []

    element = context.get_last_element_from_context_list()
    buttons = []
    if element:
        message = 'SELECT THE RELATION:'
        type_, value_list = get_element_type_and_value_list(element)
        buttons = messages.get_buttons_relation_list(type_)
    else:
        message += 'No element registered yet...'
    return {'message': message, 'buttons': buttons}


def action_view_element_info(msg=''):
    logger.info('Executing "action_view_element_info"')
    message = msg
    buttons = []

    element = context.get_last_element_from_context_list()
    if element:

        type_, value_list = get_element_type_and_value_list(element)
        if len(value_list) == 1:
            message += 'RESULT:\n'
            message += '\n'.join(['- {0} : {1}'.format(k, v) for k, v in value_list[0].items()])
    else:
        message += 'No element registered yet...'
    return {'message': message, 'buttons': buttons}


def action_view_element_attribute(attribute, position=0, msg=''):
    logger.info('Executing "action_view_element_attribute"')
    message = msg
    buttons = []

    element = context.get_last_element_from_context_list()
    if element:

        type_, value_list = get_element_type_and_value_list(element)
        element_properties = database.get_element_properties(type_)

        #  control if there is a join to do
        if attribute in extract_element_relation_attribute_list(element_properties):

            # control if there is an element in context_list
            if len(value_list) == 1:

                element_list = join_element_on_attribute(element, attribute)
                message += 'JOINING...\n'
                message += messages.get_message_word_list(attribute, element_list)

            # if there is an element or a list...
            else:

                # if position > 0, it means a selection has already been done
                if position > 0:
                    # todo: needs some checks...
                    context.add_element_to_context_list(value_list[position - 1])
                    # recursively calls itself
                    return action_view_element_attribute(attribute)

                else:
                    message += 'WHICH ONE?:\n'.format(type_)
                    payload_list = ['/view_element_{}{{"position":"{}"}}'
                                    .format(attribute, pos + 1) for pos, val in enumerate(value_list)]
                    buttons = messages.get_buttons_word_list(type_, value_list, payload_list)

        else:

            message += 'ATTRIBUTE NOT VALID\n'.format(attribute)
            return action_view_element_relation_list(message)

    else:
        message += 'No element registered yet...'

    return {'message': message, 'buttons': buttons}
