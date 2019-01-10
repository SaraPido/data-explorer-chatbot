import logging

from nltk import edit_distance
from modules.database import resolver
from modules import context
from modules.patterns import btn, msg_list, msg_simple, nlu

logger = logging.getLogger(__name__)

ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3

LIMIT = 5

# Helpers


def find_element_by_word(element_name, word):
    element_list = resolver.query_select_on_word(element_name, word)
    if element_list:
        count = len(element_list)
        element_list = element_list[:LIMIT]
        context.add_element_to_context_list(element_name + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(element_name, element_list[0])
        context.decorate_last_element_with_action_name('Elements "{}" by word "{}"'.format(element_name, word))
        return element_list, count
    else:
        return None, None  # todo: error/exception


def join_element_with_related_element(element_name, element, related_element_name, by_element_name):
    if not by_element_name:
        element_list = resolver.query_simple_join_with_related_element(element_name, element, related_element_name)
    else:
        element_list, todo = resolver.query_double_join_with_related_element(element_name, element,
                                                                             related_element_name, by_element_name)
    count = len(element_list)
    element_list = element_list[:LIMIT]
    if element_list:
        context.add_element_to_context_list(related_element_name + '_list', element_list)
        if len(element_list) == 1:
            context.add_element_to_context_list(related_element_name, element_list[0])
        # todo: the "by_element_name"
        context.decorate_last_element_with_action_name('Elements "{}" related with "{}"'.format(related_element_name, element_name))
        return element_list, count
    else:
        return None, None  # todo: error/exception


def get_element_name_and_value_list(element):
    # TODO: write doc and refactor name of the method
    element_name = element['name']
    value_list = element['value']
    if element_name.endswith('_list'):
        element_name = element_name[:-5]
    else:
        value_list = [value_list]
    return element_name, value_list


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

#

#

# Actions


def action_find_element_by_word(entities, messages, buttons):

    element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    word = entities.get(nlu.ENTITY_WORD)

    if element_name and word:

        if resolver.is_element_findable_by_word(element_name):

            # when a "find" action gets called, the context list is reset
            context.reset_context_list()

            element_list, count = find_element_by_word(element_name, word)

            msg_simple.FIND_BY_WORD(messages, element_name, word)

            if not element_list:
                msg_simple.NOTHING_FOUND(messages)

            elif count == 1:
                msg_simple.ONE_RESULT_FOUND(messages)
                view_element_info(messages)

            else:
                msg_simple.COUNT_RESULTS_FOUND(messages, count)
                # parametrize this
                if count < LIMIT:
                    msg_simple.ONLY_COUNT_DISPLAYED(messages, LIMIT)  # param

                # only listing here
                msg_list.LIST_OF_ELEMENTS(messages, element_name, element_list)
                # btn.get_buttons_select_element(buttons, element_name, element_list)

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
            element_name, value_list = get_element_name_and_value_list(element)
            if len(value_list) == 1:
                messages.append('There is only one element!\n')
                view_element_info(entities, messages, buttons)

            else:
                if position <= len(value_list):
                    context.add_element_to_context_list(element_name, value_list[position - 1])
                    context.decorate_last_element_with_action_name('Selection of "{}" with position "{}"'
                                                                   .format(element_name, position))
                    view_element_info(entities, messages, buttons)
                else:
                    messages.append('I am sorry, but you are selecting an element with an index out of range!')

    else:
        msg_simple.ERROR(messages)


def view_element_info(entities, messages, buttons):

    element = context.get_last_element_from_context_list()

    if element:
        element_name, value_list = get_element_name_and_value_list(element)
        if len(value_list) == 1:
            msg_list.ELEMENT_ATTRIBUTES(messages, element_name, value_list[0])

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_view_element_relations(entities, messages, buttons):
    """
    If the context_list is not empty, it generates BUTTONS
    for the available columns to the user
    """

    element = context.get_last_element_from_context_list()

    if element:
        element_name, value_list = get_element_name_and_value_list(element)

        if len(value_list) == 1:
            messages.append('Down here the relations of TODO')
        messages.append('SELECT one relation to perform the JOIN')
        btn.get_buttons_element_relations(buttons, element_name)

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


# todo case of many-to-many
def action_view_element_related_element(entities, messages, buttons):

    related_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_ELEMENT_NAME))
    by_element_name = handle_element_name_similarity(entities.get(nlu.ENTITY_BY_ELEMENT_NAME))
    pos = entities.get(nlu.ENTITY_POSITION)

    if related_element_name:

        element = context.get_last_element_from_context_list()
        if element:

            element_name, value_list = get_element_name_and_value_list(element)
            element_properties = resolver.get_element_properties(element_name)

            #  control if there is a join to do
            if value_list and related_element_name in element_properties['relations'].keys():

                # control if there is ONLY an element in context_list
                if len(value_list) == 1:

                    element_list, count = join_element_with_related_element(element_name, value_list[0],
                                                                            related_element_name,
                                                                            by_element_name)
                    messages.append('I have just performed a JOIN! From TODO')
                    if element_list:

                        # if only one result
                        if count == 1:

                            msg_simple.ONE_RESULT_FOUND(messages)
                            view_element_info(entities, messages, buttons)

                        else:

                            msg_simple.COUNT_RESULTS_FOUND(messages, count)
                            if count > LIMIT:
                                msg_simple.ONLY_COUNT_DISPLAYED(messages, LIMIT)  # param

                            msg_list.LIST_OF_ELEMENTS(messages, related_element_name, element_list)

                    else:
                        msg_simple.NOTHING_FOUND(messages)

                # if there is an element or a list...
                else:

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

            else:

                messages.append('You cannot JOIN on attribute "{}" :('.format(related_element_name))
                action_view_element_relations(messages)

        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        msg_simple.ERROR(messages)


def action_show_context(entities, messages, buttons):

    action_name_and_position_list = context.get_action_name_and_position_list()

    if action_name_and_position_list:

        # removing the first element
        action_name = action_name_and_position_list.pop()[0]
        msg_simple.SHOW_CURRENT_ACTION_NAME_CONTEXT(messages, action_name)

        msg_simple.SHOW_CONTEXT_BUTTONS(messages)
        btn.get_buttons_go_back_to_context_position(buttons, action_name_and_position_list)

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_go_back_to_context_position(entities, messages, buttons):

    pos = entities.get(nlu.ENTITY_POSITION)

    if pos:
        position = int(pos)
        if position in [val[1] for val in context.get_action_name_and_position_list()]:
            context.go_back_to_position(position)
            element = context.get_last_element_from_context_list()
            element_name, value_list = get_element_name_and_value_list(element)
            if len(value_list) == 1:
                view_element_info(entities, messages, buttons)
            else:
                msg_list.LIST_OF_ELEMENTS(messages, element_name, value_list)
        elif position == nlu.VALUE_POSITION_RESET_CONTEXT:
            context.reset_context_list()
            msg_simple.CONTEXT_LIST_RESET(messages)
        else:
            action_show_context(entities, messages)

    else:
        action_show_context(entities, messages)


intents_to_actions = {
    nlu.INTENT_FIND_ELEMENT_BY_WORD: action_find_element_by_word.__name__,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position.__name__,
    nlu.INTENT_VIEW_RELATIONS: action_view_element_relations.__name__,
    nlu.INTENT_VIEW_RELATED_ELEMENT: action_view_element_related_element.__name__,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position.__name__,
    nlu.INTENT_SHOW_CONTEXT: action_show_context.__name__
}


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