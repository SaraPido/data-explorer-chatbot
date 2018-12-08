import logging

from modules.database import resolver
from modules import context

from modules.responses import buttons as btn


logger = logging.getLogger(__name__)


# Helpers


def find_element_by_word(element_type, word):
    element_list = resolver.query_select_on_word(element_type, word)
    if element_list:
        context.add_element_to_context_list(element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_type, element_list[0])
        return element_list
    else:
        return None  # todo: error/exception


def join_element_on_attribute(element_type, element, attribute):
    element_list = resolver.query_select_join_on_attribute(element_type, element, attribute)
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


def extract_element_word_string(element_type, element):
    word_list = resolver.get_element_properties(element_type)['word_list']
    return ' '.join(element[x] for x in word_list)


def extract_element_relation_list(element_properties):
    return [e['type'] for e in element_properties['relation_list']]


#

#

# Actions


def action_find_element_by_word(element_type, word, messages=None):
    if messages is None:
        messages = []
    logger.info('Executing "action_find_element_by_word"')
    buttons = []

    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    messages.append('If I am right, you are looking for...\n'
                    'Element: {}\n'
                    'By word: "{}"\n'
                    'Let me check if it is present the database...\n'.format(element_type.upper(), word))
    element_list = find_element_by_word(element_type, word)

    if not element_list:
        messages.append('Nothing has been found, I am sorry!'.format(element_type, word))

    elif len(element_list) == 1:
        messages.append('I have found one result!')
        return action_view_element_info(messages)

    else:
        messages.append('Multiple results have been found!\n'
                        'If you want more information, SELECT one result.')
        buttons = btn.get_buttons_select_element(element_type, element_list)

    return {'messages': messages, 'buttons': buttons}


def action_select_element_by_position(position: int, messages=None):
    if messages is None:
        messages = []
    logger.info('Executing "action_select_element_by_position"')
    buttons = []

    element = context.get_last_element_from_context_list()

    if element:
        type_, value_list = get_element_type_and_value_list(element)
        if len(value_list) == 1:
            messages.append('There is only one element!\n')
            action_view_element_info(messages)
        else:
            if position <= len(value_list):
                context.add_element_to_context_list(type_, value_list[position - 1])
                return action_view_element_info()
            else:
                messages.append('I am sorry, but you are selecting an element with an index out of range!')

    return {'messages': messages, 'buttons': buttons}


def action_view_element_info(messages=None):
    if messages is None:
        messages = []
    logger.info('Executing "action_view_element_info"')
    buttons = []

    element = context.get_last_element_from_context_list()
    if element:

        type_, value_list = get_element_type_and_value_list(element)
        if len(value_list) == 1:
            msg = '{}: "{}"\n'.format(type_.upper(), extract_element_word_string(type_, value_list[0]))
            msg += '\n'.join(['- {0}: {1}'.format(k, v) for k, v in value_list[0].items()])
            messages.append(msg)
    else:
        messages.append('No element registered yet, I am sorry!')

    return {'messages': messages, 'buttons': buttons}


def action_view_element_relation_list(messages=None):
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    if messages is None:
        messages = []
    logger.info('Executing "action_view_element_relation_list"')
    buttons = []

    element = context.get_last_element_from_context_list()
    buttons = []
    if element:
        type_, value_list = get_element_type_and_value_list(element)

        if len(value_list) == 1:
            word_elements = ', '.join(extract_element_word_string(type_, el) for el in value_list)
            messages.append('Down here the relations of:\n'
                            '{}: "{}"'.format(type_.upper(), word_elements))
        messages.append('SELECT one relation to perform the JOIN')
        buttons = btn.get_buttons_relation_list(type_)

    else:
        messages.append('No element registered yet, I am sorry!')
    return {'messages': messages, 'buttons': buttons}


def action_view_element_related_element(related_element_type, position=0, messages=None):
    if messages is None:
        messages = []
    logger.info('Executing "action_view_element_attribute"')
    buttons = []

    element = context.get_last_element_from_context_list()
    if element:

        type_, value_list = get_element_type_and_value_list(element)
        element_properties = resolver.get_element_properties(type_)

        #  control if there is a join to do
        if related_element_type in extract_element_relation_list(element_properties):

            # control if there is an element in context_list
            if len(value_list) == 1:

                element_list = join_element_on_attribute(type_, value_list[0], related_element_type)
                messages.append('I have just performed a JOIN! From:\n'
                                '{}: "{}"'.format(type_.upper(), extract_element_word_string(type_, value_list[0])))
                if element_list:

                    # if only one result
                    if len(element_list) == 1:

                        messages.append('I have found only one result!')
                        return action_view_element_info(messages)

                    else:

                        messages.append('Multiple results have been found!\n'
                                        'If you want more information, SELECT one result.')
                        buttons = btn.get_buttons_select_element(related_element_type, element_list)

                else:
                    messages.append('Nothing has been found!')

            # if there is an element or a list...
            else:

                # if position > 0, it means a selection has already been done
                if position > 0:
                    # todo: needs some checks...
                    context.add_element_to_context_list(type_, value_list[position - 1])
                    # recursively calls itself
                    return action_view_element_related_element(related_element_type)

                else:
                    messages.append('There is more than one element on which you can perform the JOIN!\n'
                                    'Please SELECT the one you are interested in.'.format(type_))
                    payload_list = ['/view_related_element{{"element":"{}", "position":"{}"}}'
                                    .format(related_element_type, pos + 1) for pos in range(len(value_list))]
                    buttons = btn.get_buttons_word_list(type_, value_list, payload_list)

        else:

            messages.append('You cannot JOIN on this attribute :('.format(related_element_type))
            return action_view_element_relation_list(messages)

    else:
        messages.append('No element registered yet...')

    return {'messages': messages, 'buttons': buttons}
