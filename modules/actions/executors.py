import logging

from nltk import edit_distance

from modules.database import resolver
from modules import context

from modules.patterns import buttons as btn, msg_list, msg_simple, nlu

logger = logging.getLogger(__name__)

ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3

LIMIT = 5


# Helpers


def find_element_by_word(element_type, word):
    element_list = resolver.query_select_on_word(element_type, word)
    if element_list:
        count = len(element_list)
        element_list = element_list[:LIMIT]
        context.add_element_to_context_list(element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_type, element_list[0])
        context.decorate_last_element_with_action_name('Elements "{}" by word "{}"'.format(element_type, word))
        return element_list, count
    else:
        return None, None  # todo: error/exception


def join_element_with_related_element(element_type, element, related_element_type, by):
    if not by:
        element_list = resolver.query_simple_join_with_related_element(element_type, element, related_element_type)
    else:
        element_list, todo = resolver.query_double_join_with_related_element(element_type, element,
                                                                             related_element_type, by)
    count = len(element_list)
    element_list = element_list[:LIMIT]
    if element_list:
        context.add_element_to_context_list(related_element_type + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(related_element_type, element_list[0])
        # todo: the "by"
        context.decorate_last_element_with_action_name('Elements "{}" related with "{}"'.format(related_element_type, element_type))
        return element_list, count
    else:
        return None, None  # todo: error/exception


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
    word_column_list = resolver.get_element_properties(element_type)['word_column_list']
    return ' '.join(element[x] for x in word_column_list)


#

#

# Actions


def action_find_element_by_word(entities, messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_find_element_by_word"')
    buttons = []

    element_type = handle_element_type_similarity(entities.get(nlu.ENTITY_ELEMENT_TYPE))
    word = entities.get(nlu.ENTITY_WORD)

    if element_type and word:

        if resolver.is_element_type_findable_by_word(element_type):

            # when a "find" action gets called, the context list is reset
            context.reset_context_list()

            element_list, count = find_element_by_word(element_type, word)

            msg_simple.FIND_BY_WORD(messages, element_type, word)

            if not element_list:
                msg_simple.NOTHING_FOUND(messages)

            elif count == 1:
                msg_simple.ONE_RESULT_FOUND(messages)
                return action_view_element_info(messages)

            else:
                msg_simple.COUNT_RESULTS_FOUND(messages, count)
                # parametrize this
                if count < LIMIT:
                    msg_simple.ONLY_COUNT_DISPLAYED(messages, LIMIT)  # param

                # only listing here
                msg_list.LIST_OF_ELEMENTS(messages, element_type, element_list)
                # buttons = btn.get_buttons_select_element(element_type, element_list)

        else:
            msg_simple.ELEMENT_TYPE_NOT_FINDABLE_BY_WORD(messages, element_type)

    else:
        msg_simple.ERROR(messages)

    return {'messages': messages, 'buttons': buttons}


def action_select_element_by_position(entities, messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_select_element_by_position"')
    buttons = []

    pos = entities.get(nlu.ENTITY_POSITION)

    if pos:
        position = int(pos)

        element = context.get_last_element_from_context_list()

        if element:
            type_, value_list = get_element_type_and_value_list(element)
            if len(value_list) == 1:
                messages.append('There is only one element!\n')
                action_view_element_info(messages)

            else:
                if position <= len(value_list):
                    context.add_element_to_context_list(type_, value_list[position - 1])
                    context.decorate_last_element_with_action_name('Selection of "{}" with position "{}"'
                                                                   .format(type_, position))
                    return action_view_element_info()
                else:
                    messages.append('I am sorry, but you are selecting an element with an index out of range!')

    else:
        msg_simple.ERROR(messages)

    return {'messages': messages, 'buttons': buttons}


def action_view_element_info(messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_view_element_info"')
    buttons = []

    element = context.get_last_element_from_context_list()

    if element:
        type_, value_list = get_element_type_and_value_list(element)
        if len(value_list) == 1:
            msg_list.ELEMENT_ATTRIBUTES(messages, type_, value_list[0])

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)

    return {'messages': messages, 'buttons': buttons}


def action_view_element_relation_list(messages=None):
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """
    messages = messages if messages else []
    logger.info('Executing "action_view_element_relation_list"')
    buttons = []

    element = context.get_last_element_from_context_list()

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


# todo case of many-to-many
def action_view_element_related_element(entities, messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_view_element_attribute"')
    buttons = []

    related_element_type = handle_element_type_similarity(entities.get(nlu.ENTITY_ELEMENT_TYPE))
    by_element_type = handle_element_type_similarity(entities.get(nlu.ENTITY_BY_ELEMENT_TYPE))
    pos = entities.get(nlu.ENTITY_POSITION)

    if related_element_type:

        element = context.get_last_element_from_context_list()
        if element:

            type_, value_list = get_element_type_and_value_list(element)
            element_properties = resolver.get_element_properties(type_)

            #  control if there is a join to do
            if value_list and related_element_type in [e['type'] for e in element_properties['relation_list']]:

                # control if there is ONLY an element in context_list
                if len(value_list) == 1:

                    element_list, count = join_element_with_related_element(type_, value_list[0], related_element_type,
                                                                            by_element_type)
                    messages.append('I have just performed a JOIN! From:\n'
                                    '{}: "{}"'.format(type_.upper(), extract_element_word_string(type_, value_list[0])))
                    if element_list:

                        # if only one result
                        if count == 1:

                            msg_simple.ONE_RESULT_FOUND(messages)
                            return action_view_element_info(messages)

                        else:

                            msg_simple.COUNT_RESULTS_FOUND(messages, count)
                            if count > LIMIT:
                                msg_simple.ONLY_COUNT_DISPLAYED(messages, LIMIT)  # param

                            msg_list.LIST_OF_ELEMENTS(messages, related_element_type, element_list)

                    else:
                        msg_simple.NOTHING_FOUND(messages)

                # if there is an element or a list...
                else:

                    position = int(pos) if pos else 0
                    # if position > 0, it means a selection has already been done
                    if position > 0:
                        # todo: needs some checks...
                        context.add_element_to_context_list(type_, value_list[position - 1])
                        # todo: review this decoration
                        context.decorate_last_element_with_action_name('Selection of "{}" with position "{}"'
                                                                       .format(type_, position))
                        # recursively calls itself
                        return action_view_element_related_element(related_element_type)

                    else:

                        # todo: the multijoin!
                        messages.append('TODO the multi-join: joining multiple elements!')

            else:

                messages.append('You cannot JOIN on this attribute :('.format(related_element_type))
                return action_view_element_relation_list(messages)

        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    return {'messages': messages, 'buttons': buttons}


# helper

def handle_element_type_similarity(element_type_received):
    winner = None
    all_elements_type = resolver.get_all_element_types()
    if element_type_received:
        if element_type_received in all_elements_type:
            winner = element_type_received
        else:
            logger.info('I will compute some similarity distance '
                        'for the received element "{}"...'.format(element_type_received))
            sim = 100  # very high number
            for el_type in all_elements_type:
                received = element_type_received
                cur = edit_distance(el_type, received)
                if cur < sim and cur < ELEMENT_SIMILARITY_DISTANCE_THRESHOLD:
                    sim = cur
                    winner = el_type
            logger.info('...I decided on: {}, with similarity distance: {}'.format(winner, sim))
    return winner


def action_show_context(entities, messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_show_context"')
    buttons = []

    action_name_and_position_list = context.get_action_name_and_position_list()
    if action_name_and_position_list:

        # removing the first element
        action_name = action_name_and_position_list.pop()[0]
        msg_simple.SHOW_CURRENT_ACTION_NAME_CONTEXT(messages, action_name)

        msg_simple.SHOW_CONTEXT_BUTTONS(messages)
        buttons = btn.get_buttons_go_back_to_context_position(action_name_and_position_list)

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)

    return {'messages': messages, 'buttons': buttons}


def action_go_back_to_context_position(entities, messages=None):
    messages = messages if messages else []
    logger.info('Executing "action_show_context"')
    buttons = []

    pos = entities.get(nlu.ENTITY_POSITION)
    if pos:
        position = int(pos)
        if position in [val[1] for val in context.get_action_name_and_position_list()]:
            context.go_back_to_position(position)
            element = context.get_last_element_from_context_list()
            type_, value_list = get_element_type_and_value_list(element)
            if len(value_list) == 1:
                return action_view_element_info(messages)
            else:
                msg_list.LIST_OF_ELEMENTS(messages, type_, value_list)
        elif position == nlu.VALUE_POSITION_RESET_CONTEXT:
            context.reset_context_list()
            msg_simple.CONTEXT_LIST_RESET(messages)
        else:
            return action_show_context(entities, messages)
    else:
        return action_show_context(entities, messages)

    return {'messages': messages, 'buttons': buttons}



