import logging

from server.core import database
from server.core import context
from server.core.actions import messages





# Helpers

def find_element_by_word(element_type, word):
    element_list = database.query_select_on_word(element_type, word)
    if element_list:
        context.add_element_to_context_list(element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_type, element_list[0])
        return element_list
    else:
        return None # todo: error/exception


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

#

# Actions


def run_action_find_element_by_word(self, dispatcher, tracker, domain, element_type):
    word = next(tracker.get_latest_entity_values('word'), None)

    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    if word:
        element_list = find_element_by_word(element_type, word)
        if not element_list:
            message = 'Nothing has been found with: ' + word
        else:
            message = 'Here the results for {}:\n'.format(element_type)
            message += messages.get_message_word_list(element_type, element_list)
    else:
        message = "No words entity has been received..."
    dispatcher.utter_message(message)

    return []


# todo: maybe all this way....
def action_find_element_by_word(element_type, word):
    # when a "find" action gets called, the context list is reset
    context.reset_context_list()

    if word:
        element_list = find_element_by_word(element_type, word)
        if not element_list:
            message = 'Nothing has been found with: ' + word
        else:
            message = 'Here the results for {}:\n'.format(element_type)
            message += messages.get_message_word_list(element_type, element_list)
    else:
        message = "No words entity has been received..."
    return {'response': message}


# todo: maybe all this way....
def action_view_element_column_list():
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    element = context.get_last_element_from_context_list()
    buttons = []
    if element:
        message = 'Click the desired column:'
        type_, value_list = get_element_type_and_value_list(element)
        column_list = database.get_element_column_list(type_)
        # little trick to remove 'word' columns from the available
        word_list = database.get_element_word_list(type_)
        column_list = [e for e in column_list if e not in word_list]
        foreign_key_list = database.get_element_foreign_key_list(type_)
        relation_list = database.get_element_relation_list(type_)
        for col in column_list:
            if col not in foreign_key_list:
                buttons.append({'title': col, 'payload': '/view_element_' + col})
        for rel in relation_list:
            buttons.append({'title': rel['type'], 'payload': '/view_element_' + rel['type']})
    else:
        message = 'The context_list is empty!'
    return {'response': message, 'buttons': buttons}



def run_action_view_element_column_list(self, dispatcher, tracker, domain):
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    element = context.get_last_element_from_context_list()
    buttons = []
    if element:
        message = 'Click the desired column:'
        type_, value_list = get_element_type_and_value_list(element)
        column_list = database.get_element_column_list(type_)
        # little trick to remove 'word' columns from the available
        word_list = database.get_element_word_list(type_)
        column_list = [e for e in column_list if e not in word_list]
        foreign_key_list = database.get_element_foreign_key_list(type_)
        relation_list = database.get_element_relation_list(type_)
        for col in column_list:
            if col not in foreign_key_list:
                buttons.append({'title': col, 'payload': '/view_element_' + col})
        for rel in relation_list:
            buttons.append({'title': rel['type'], 'payload': '/view_element_' + rel['type']})
    else:
        message = 'The context_list is empty!'
    dispatcher.utter_button_message(message, buttons)
    return []


def run_action_view_element_attribute(self, dispatcher, tracker, domain, attribute_type):
    element = context.get_last_element_from_context_list()
    if element:
        type_, value_list = get_element_type_and_value_list(element)
        if attribute_type in database.get_element_column_list(type_):
            message = 'Results for attribute {}:\n'.format(attribute_type)
            message += messages.get_message_word_list_with_attribute(type_, value_list, attribute_type)
            dispatcher.utter_message(message)
        else:
            message = 'The specified attribute is not part of ' + type_
            dispatcher.utter_message(message)
            run_action_view_element_column_list(self, dispatcher, tracker, domain)
    else:
        message = 'The context_list is empty!'
        dispatcher.utter_message(message)
    return []
