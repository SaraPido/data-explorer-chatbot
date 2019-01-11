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


# Actions


def action_find_element_by_word(entities, messages, buttons):
    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    word = entities.get(nlu.ENTITY_WORD)

    if element_name and word:

        if resolver.is_element_findable_by_word(element_name):

            # when a "find" action gets called, the context list is reset
            context.reset_context_list()

            element = resolver.query_select_on_word(element_name, word)

            if element['value']:

                element['action_description'] = 'Elements of type ' + element_name + ' by word ' + word

                element['value'] = element['value'][:LIMIT]
                context.add_element_to_context_list(element)

                msg_simple.FIND_BY_WORD(messages, element_name, word)

                if element['real_value_length'] == 1:
                    msg_simple.ONE_RESULT_FOUND(messages)
                    context.add_element_to_context_list(element)
                    view_element_info(messages)

                else:
                    msg_simple.N_RESULTS_FOUND(messages, element['real_value_length'])
                    # parametrize this
                    if element['real_value_length'] > LIMIT:
                        msg_simple.ONLY_N_DISPLAYED(messages, LIMIT)  # param

                    msg_list.LIST_OF_ELEMENTS(messages, element)
                    # btn.get_buttons_select_element(buttons, element_name, element_list

            else:
                msg_simple.NOTHING_FOUND(messages)

        else:
            msg_simple.ELEMENT_NAME_NOT_FINDABLE_BY_WORD(messages, element_name)

    else:

        msg_simple.ERROR(messages)


def action_select_element_by_position(entities, messages, buttons):
    pos = entities.get(nlu.ENTITY_POSITION)

    if pos:
        position = int(pos)

        element = context.get_last_element_from_context_list()

        if element:

            if element['real_value_length'] == 1:
                messages.append('There is only one element!\n')
                view_element_info(entities, messages, buttons)

            else:
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
                    view_element_info(entities, messages, buttons)
                else:
                    messages.append('I am sorry, but you are selecting an element with an index out of range!')

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

        if element['real_value_length'] == 1:
            messages.append('Down here the relations of TODO')
            messages.append('SELECT one relation to perform the JOIN')
            btn.get_buttons_element_relations(buttons, element['element_name'])
        else:
            messages.append('NO MULTI-JOIN ALLOWED -  TODO')

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_view_element_related_element(entities, messages, buttons):
    related_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    by_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_BY_ELEMENT_NAME))
    # pos = entities.get(nlu.ENTITY_POSITION)

    if related_element_name:

        element = context.get_last_element_from_context_list()
        if element:

            element_properties = resolver.get_element_properties(element['element_name'])

            #  control if there is a join to do
            if related_element_name in element_properties['relations'].keys():

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

                        # if only one result
                        if result_element['real_value_length'] == 1:

                            msg_simple.ONE_RESULT_FOUND(messages)
                            view_element_info(entities, messages, buttons)

                        else:

                            msg_simple.N_RESULTS_FOUND(messages, result_element['real_value_length'])
                            if result_element['real_value_length'] > LIMIT:
                                msg_simple.ONLY_N_DISPLAYED(messages, LIMIT)  # param

                            msg_list.LIST_OF_ELEMENTS(messages, result_element)

                    else:
                        msg_simple.NOTHING_FOUND(messages)

                # if there is an element or a list...
                else:

                    messages.append("TODO SELECT AND MAKE JOIN")
                    """
                    position = int(pos) if pos else 0
                    # if position > 0, it means a selection has already been done
                    if position > 0:
                        # todo: needs some checks...
                        context.add_element_to_context_list(element_name, value_list[position - 1])
                        # todo: review this decoration
                        context.decorate_last_element_with_action_name('Selection of "{}" with position "{}"'
                                                                       .format(element_name, position))
                        # recursively calls itself
                        action_view_element_related_element(entities, messages, buttons)

                    else:

                        # todo: the multijoin!
                        messages.append('TODO the multi-join: joining multiple elements!')
                    """
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
        position = int(pos)

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


intents_to_actions = {
    nlu.INTENT_FIND_ELEMENT_BY_WORD: action_find_element_by_word.__name__,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position.__name__,
    nlu.INTENT_VIEW_RELATIONS: action_view_element_relations.__name__,
    nlu.INTENT_VIEW_RELATED_ELEMENT: action_view_element_related_element.__name__,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position.__name__,
    nlu.INTENT_SHOW_CONTEXT: action_show_context.__name__
}


# MAIN IMPORTANT methods


def execute_action_from_intent_name(intent_name, entities):
    messages = []
    buttons = []
    action_name = intents_to_actions.get(intent_name)
    if action_name:
        logger.info('Executing action: "' + action_name + '"')
        globals()[action_name](entities, messages, buttons)
        return {'messages': messages, 'buttons': buttons}
    else:
        return execute_fallback()


def execute_fallback():
    messages = []
    msg_simple.ERROR(messages)
    return {'messages': messages}
