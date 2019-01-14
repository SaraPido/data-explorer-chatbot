import logging

from nltk import edit_distance
from modules.database import resolver
from modules import context
from modules.patterns import btn, msg_list, msg_simple, nlu

logger = logging.getLogger(__name__)

ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3

LIMIT = 5


# Helpers


def handle_element_name_similarity(element_name_received):
    winner = None
    all_elements_names = resolver.get_all_element_names()
    if element_name_received:
        if element_name_received in all_elements_names:
            winner = element_name_received
        else:
            logger.info('I will compute some similarity distance '
                        'for the received element "{}"...'.format(element_name_received))
            sim = 100  # very high number
            for el_name in all_elements_names:
                received = element_name_received
                cur = edit_distance(el_name, received)
                if cur < sim and cur < ELEMENT_SIMILARITY_DISTANCE_THRESHOLD:
                    sim = cur
                    winner = el_name
            logger.info('...I decided on: {}, with similarity distance: {}'.format(winner, sim))
    return winner


def handle_quantity_result_elements(entities, messages, buttons, element):

    if element['real_value_length'] == 1:
        msg_simple.ONE_RESULT_FOUND(messages)
        view_element_info(entities, messages, buttons)

    else:
        msg_simple.N_RESULTS_FOUND(messages, element['real_value_length'])
        # parametrize this
        if element['real_value_length'] > LIMIT:
            msg_simple.ONLY_N_DISPLAYED(messages, LIMIT)  # param

        msg_list.LIST_OF_ELEMENTS(messages, element)


def handle_element_selection(element, position):

    if 0 < position <= len(element['value']):  # element['real_value_length']:
        # copying the dictionary
        selected_element = dict(element)

        # I must save it as a list
        selected_element['value'] = [element['value'][position - 1]]

        selected_element['query'] = None
        selected_element['real_value_length'] = 1
        selected_element['action_description'] = 'Selected element of type ' + element['element_name'] + \
                                                 ' at position ' + str(position)

        context.add_element_to_context_list(selected_element)
        return True

    return False

# Actions


# FIND ACTIONS


def action_find_element_by_word(entities, messages, buttons):
    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    word = entities.get(nlu.ENTITY_WORD)

    if element_name and word:

        if resolver.is_element_findable_by_word(element_name, directly=True):

            # when a "find" action gets called, the context list is reset
            context.reset_context_list()

            element = resolver.query_select_on_word(element_name, word, '=')

            if element['value']:

                element['action_description'] = 'Elements ' + element_name + ' by word ' + word

                element['value'] = element['value'][:LIMIT]
                context.add_element_to_context_list(element)

                msg_simple.FIND_BY_WORD(messages, element_name, word)

                handle_quantity_result_elements(entities, messages, buttons, element)

                action_view_element_relations(entities, messages, buttons)

            else:
                msg_simple.NOTHING_FOUND(messages)

        else:
            msg_simple.ELEMENT_NOT_FINDABLE_BY_WORD(messages, element_name)

    else:

        msg_simple.ERROR(messages)


def action_find_element_by_number(entities, messages, buttons):
    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    number = entities.get(nlu.ENTITY_NUMBER)
    operator = entities.get(nlu.ENTITY_OPERATOR)

    if element_name and number:

        if resolver.is_element_findable_by_number(element_name, directly=True):

            # when a "find" action gets called, the context list is reset
            context.reset_context_list()

            # TODO maybe work more on this concept
            operator = operator if operator in {'=', '>', '<'} else '='

            element = resolver.query_select_on_number(element_name, number, operator)

            if element['value']:

                element['action_description'] = 'Elements ' + element_name + ' by number ' + number

                element['value'] = element['value'][:LIMIT]
                context.add_element_to_context_list(element)

                msg_simple.FIND_BY_NUMBER(messages, element_name, number)

                handle_quantity_result_elements(entities, messages, buttons, element)

                action_view_element_relations(entities, messages, buttons)

            else:
                msg_simple.NOTHING_FOUND(messages)

        else:
            msg_simple.ELEMENT_NOT_FINDABLE_BY_NUMBER(messages, element_name)

    else:

        msg_simple.ERROR(messages)


def action_find_el_by_related_word(entities, messages, buttons):
    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    related_element_name = entities.get(nlu.ENTITY_RELATED_ELEMENT_NAME)
    word = entities.get(nlu.ENTITY_WORD)

    if element_name and related_element_name and word:

        # this time I check if the RELATED element is findable by word
        if resolver.is_element_findable_by_word(related_element_name):

            # todo need to pay attention to many to many joins!!! now it causes problem when multijoin has more paths
            if resolver.are_elements_related(element_name, related_element_name):

                element = resolver.query_select_on_related_element_word(element_name, related_element_name, word, '=')

                if element['value']:

                    element['action_description'] = 'Elements ' + element_name + ' related with ' + \
                                                    related_element_name + ' by word ' + word

                    element['value'] = element['value'][:LIMIT]
                    context.add_element_to_context_list(element)

                    msg_simple.FIND_BY_RELATED_ELEMENT_WORD(messages, element_name, related_element_name, word)

                    handle_quantity_result_elements(entities, messages, buttons, element)

                    action_view_element_relations(entities, messages, buttons)

                else:
                    msg_simple.NOTHING_FOUND(messages)

            else:
                # todo: elements not related message
                messages.append('elements not related')

        else:
            msg_simple.ELEMENT_NOT_FINDABLE_BY_WORD(messages, element_name)

    else:
        msg_simple.ERROR(messages)


def action_find_el_by_related_number(entities, messages, buttons):
    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    related_element_name = entities.get(nlu.ENTITY_RELATED_ELEMENT_NAME)
    number = entities.get(nlu.ENTITY_NUMBER)

    operator = entities.get(nlu.ENTITY_OPERATOR)

    if element_name and related_element_name and number:

        # this time I check if the RELATED element is findable by word
        if resolver.is_element_findable_by_number(related_element_name):

            if resolver.are_elements_related(element_name, related_element_name):

                # TODO maybe work more on this concept
                operator = operator if operator in {'=', '>', '<'} else '='

                element = resolver.query_select_on_related_element_number(element_name, related_element_name, number,
                                                                          operator)

                if element['value']:

                    element['action_description'] = 'Elements ' + element_name + ' related with ' + \
                                                    related_element_name + ' by number ' + number

                    element['value'] = element['value'][:LIMIT]
                    context.add_element_to_context_list(element)

                    msg_simple.FIND_BY_RELATED_ELEMENT_NUMBER(messages, element_name, related_element_name, number)

                    handle_quantity_result_elements(entities, messages, buttons, element)

                    action_view_element_relations(entities, messages, buttons)

                else:
                    msg_simple.NOTHING_FOUND(messages)

            else:
                # todo: elements not related message
                messages.append('elements not related')

        else:
            msg_simple.ELEMENT_NOT_FINDABLE_BY_WORD(messages, element_name)

    else:
        msg_simple.ERROR(messages)


# SELECT ACTIONS


def action_select_element_by_position(entities, messages, buttons):
    pos = entities.get(nlu.ENTITY_POSITION)

    if pos:
        # attention, I suppose "position" is in the form "1st", "2nd", ...
        position = int(pos[:-2])

        element = context.get_last_element_from_context_list()

        if element:

            if element['real_value_length'] == 1:
                messages.append('There is only one element!\n')
                view_element_info(entities, messages, buttons)

            else:
                if handle_element_selection(element, position):
                    view_element_info(entities, messages, buttons)
                else:
                    messages.append('I am sorry, but you are selecting an element with an index out of range!')

        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        msg_simple.ERROR(messages)


def view_element_info(entities, messages, buttons):
    element = context.get_last_element_from_context_list()

    if element and element['real_value_length'] == 1:
        msg_list.ELEMENT_ATTRIBUTES(messages, element)

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_view_element_relations(entities, messages, buttons):
    element = context.get_last_element_from_context_list()

    if element:

        messages.append('Down here the relations of ' + element['element_name'])
        messages.append('SELECT one relation to perform the JOIN')
        btn.get_buttons_element_relations(buttons, element['element_name'])

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_view_element_related_element(entities, messages, buttons):
    related_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_RELATED_ELEMENT_NAME))
    by_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_BY_ELEMENT_NAME))
    pos = entities.get(nlu.ENTITY_POSITION)

    if related_element_name:

        element = context.get_last_element_from_context_list()
        if element:

            #  control if there is a join to do
            if resolver.are_elements_related(element['element_name'], related_element_name, by_element_name):

                # control if there is ONLY an element in context_list
                if element['real_value_length'] == 1:

                    result_element = resolver.query_join_with_related_element(element,
                                                                              related_element_name,
                                                                              by_element_name)

                    messages.append('I have just performed a JOIN! From TODO')
                    if result_element['value']:

                        result_element['action_description'] = 'Elements ' + related_element_name + \
                                                               ' related with ' + element['element_name']
                        result_element['value'] = result_element['value'][:LIMIT]
                        context.add_element_to_context_list(result_element)

                        handle_quantity_result_elements(entities, messages, buttons, result_element)

                        action_view_element_relations(entities, messages, buttons)

                    else:
                        msg_simple.NOTHING_FOUND(messages)

                # if there is an element or a list...
                else:

                    # if the position is not chosen yet, present the buttons
                    if not pos:
                        messages.append("SELECT on which one you want to perform the join")
                        btn.get_buttons_view_related_element_by_pos(buttons, element,
                                                                    related_element_name, by_element_name)
                    else:

                        position = int(pos[:-2])
                        if handle_element_selection(element, position):
                            # recursively calls itself
                            action_view_element_related_element(entities, messages, buttons)
                        else:
                            # TODO
                            messages.append('Something went wrong!')

            else:

                messages.append('You cannot JOIN on attribute "{}" :('.format(related_element_name))
                action_view_element_relations(entities, messages, buttons)

        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        msg_simple.ERROR(messages)


def action_show_context(entities, messages, buttons):
    action_name_list = context.get_action_name_list()

    if action_name_list:

        # removing the last element
        action_name = action_name_list.pop()
        msg_simple.SHOW_CONTEXT_INFO(messages)
        msg_simple.SHOW_CURRENT_ACTION_NAME_CONTEXT(messages, action_name)
        btn.get_buttons_go_back_to_context_position(buttons, action_name_list)

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_go_back_to_context_position(entities, messages, buttons):
    pos = entities.get(nlu.ENTITY_POSITION)

    if pos:
        position = int(pos[:-2])

        # if context is not empty
        if context.get_action_name_list():

            if position == nlu.VALUE_POSITION_RESET_CONTEXT:
                context.reset_context_list()
                msg_simple.CONTEXT_LIST_RESET(messages)

            elif position - 1 < len(context.get_action_name_list()):
                context.go_back_to_position(position)
                element = context.get_last_element_from_context_list()
                if element['real_value_length'] == 1:
                    view_element_info(entities, messages, buttons)
                else:
                    msg_list.LIST_OF_ELEMENTS(messages, element)

            else:
                # the selection is wrong, maybe create a message for this
                action_show_context(entities, messages, buttons)
        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        action_show_context(entities, messages, buttons)


intents_to_action_functions = {
    nlu.INTENT_FIND_ELEMENT_BY_WORD: action_find_element_by_word,
    nlu.INTENT_FIND_ELEMENT_BY_NUMBER: action_find_element_by_number,
    nlu.INTENT_FIND_ELEMENT_BY_RELATED_WORD: action_find_el_by_related_word,
    nlu.INTENT_FIND_ELEMENT_BY_RELATED_NUMBER: action_find_el_by_related_number,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position,
    nlu.INTENT_VIEW_RELATIONS: action_view_element_relations,
    nlu.INTENT_VIEW_RELATED_ELEMENT: action_view_element_related_element,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position,
    nlu.INTENT_SHOW_CONTEXT: action_show_context
}


# MAIN IMPORTANT methods


def execute_action_from_intent_name(intent_name, entities):
    messages = []
    buttons = []
    action_function = intents_to_action_functions.get(intent_name)
    if action_function:
        logger.info('Executing action: "' + action_function.__name__ + '"')
        action_function(entities, messages, buttons)
        return {'messages': messages, 'buttons': buttons}
    else:
        logger.info('Action related to intent "' + intent_name + '" NOT FOUND')
        return execute_fallback()


def execute_fallback():
    messages = []
    msg_simple.ERROR(messages)
    logger.info('Executing FALLBACK')
    return {'messages': messages}
