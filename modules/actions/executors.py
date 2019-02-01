import logging

from nltk import edit_distance
from modules.database import resolver
from modules import context
from modules.patterns import btn, msg_list, msg_simple, nlu

logger = logging.getLogger(__name__)

ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3
LIMIT = 5


# Helpers

def extract_entities(entities, entity_name):
    found = []
    for e in entities:
        if e.get('entity') == entity_name:
            found.append(e)
    return found


def handle_element_name_similarity(element_name_received):
    all_elements_names = resolver.get_all_element_names()
    return handle_similarity(element_name_received, all_elements_names)


def handle_element_relations_similarity(element_name, relation_name_received):
    relations = resolver.extract_relations(element_name)
    all_relations_names = [r['keyword'] for r in relations]
    return handle_similarity(relation_name_received, all_relations_names)


def handle_similarity(keyword, keyword_list):
    winner = None
    if keyword:
        if keyword in keyword_list:
            winner = keyword
        else:
            logger.info('I will compute some similarity distance '
                        'for the received element "{}"...'.format(keyword))
            sim = 100  # very high number
            for el_name in keyword_list:
                received = keyword
                cur = edit_distance(el_name, received)
                if cur < sim and cur < ELEMENT_SIMILARITY_DISTANCE_THRESHOLD:
                    sim = cur
                    winner = el_name
            logger.info('...I decided on: {}, with similarity distance: {}'.format(winner, sim))
    return winner


def handle_quantity_result_elements(entities, messages, buttons, element):

    if element['real_value_length'] == 1:
        msg_simple.ONE_RESULT_FOUND(messages)

    else:
        msg_simple.N_RESULTS_FOUND(messages, element['real_value_length'])


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


# ACTIONS


def action_find_element_by_attribute(entities, messages, buttons):

    # todo handle case no element is extracted
    extracted_element_name = extract_entities(entities, nlu.ENTITY_ELEMENT)[0]['value']
    element_name = handle_element_name_similarity(extracted_element_name)

    # todo: handle similary also for attributes...

    # >----
    # TODO: the complex case will consider multiple attributes
    attrss = extract_entities(entities, 'attr') # nlu.ENTITY_ATTRIBUTE
    words = extract_entities(entities, nlu.ENTITY_WORD)
    nums = extract_entities(entities, nlu.ENTITY_NUMBER)
    attr = attrss[0]['value'] if attrss else None
    word = words[0]['value'] if words else None
    num = nums[0]['value'] if nums else None
    # ----<

    if element_name:
        attributes = []
        for a in resolver.extract_attributes(element_name):
            # if the attribute is the one extracted
            if a.get('keyword') == attr:
                if a.get('type') == 'word' and word:
                    a['value'] = word
                    attributes.append(a)
                elif a.get('type') == 'num' and num:
                    a['value'] = num
                    attributes.append(a)

        element = resolver.query_find(element_name, attributes)

        if element['value']:
            element['action_description'] = 'TODO'

            element['value'] = element['value']  # [:LIMIT]
            context.add_element_to_context_list(element)

            msg_simple.FINDING_ELEMENT(messages)

            handle_quantity_result_elements(entities, messages, buttons, element)

            view_context_element(entities, messages, buttons)

    else:
        msg_simple.ERROR(messages)


def action_cross_relation(entities, messages, buttons):

    element = context.get_last_element_from_context_list()

    # todo handle case no element is extracted
    extracted_relation_name = extract_entities(entities, nlu.ENTITY_RELATION)[0]['value']
    relation_name = handle_element_relations_similarity(element['element_name'], extracted_relation_name)

    if element and relation_name:

        # control if there is ONLY an element in context_list
        if element['real_value_length'] == 1:

            element = resolver.query_join(element, relation_name)

            if element['value']:
                element['action_description'] = 'TODO for join'

                element['value'] = element['value']  # [:LIMIT]
                context.add_element_to_context_list(element)

                handle_quantity_result_elements(entities, messages, buttons, element)

                view_context_element(entities, messages, buttons)

            else:
                msg_simple.NOTHING_FOUND(messages)


# SELECT ACTIONS

def action_select_element_by_position(entities, messages, buttons):
    pos = extract_entities(entities, nlu.ENTITY_POSITION)[0]['value']

    if pos:
        # attention, I suppose "position" is in the form "1st", "2nd", ...
        position = int(pos[:-2])

        element = context.get_last_element_from_context_list()

        if element:

            if element['real_value_length'] == 1:
                messages.append('There is only one element!\n')
                view_context_element(entities, messages, buttons)

            else:
                if handle_element_selection(element, position):
                    view_context_element(entities, messages, buttons)
                else:
                    messages.append('I am sorry, but you are selecting an element with an index out of range!')

        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        msg_simple.ERROR(messages)


def view_context_element(entities, messages, buttons):
    element = context.get_last_element_from_context_list()

    if element:
        if element['real_value_length'] == 1:
            msg_simple.INTRODUCE_ELEMENT_TO_SHOW(messages, element['element_name'])
            msg_list.ELEMENT_ATTRIBUTES(messages, element)
            action_show_relations(entities, messages, buttons)
        else:
            if not element.get('show'):
                element['show'] = {'from': 0, 'to': min(LIMIT, element['real_value_length'])}
            show_more = element['show']['to'] < element['real_value_length']  # len(element['value'])
            if element['show']['from'] == 0:  # could not put it before.. not so pretty
                msg_simple.SELECT_FOR_INFO(messages, show_more)
            btn.get_buttons_select_element(buttons, element, show_more)
    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


def action_show_more(entities, messages, buttons):
    element = context.get_last_element_from_context_list()

    if element:
        if element['real_value_length'] > 1 and element.get('show'):
            element['show'] = {'from':  element['show']['from'] + LIMIT,
                               'to': min(element['real_value_length'], element['show']['to'] + LIMIT)}
            view_context_element(entities, messages, buttons)
        else:
            msg_simple.ERROR(messages)  # should not happen


def action_show_relations(entities, messages, buttons):
    element = context.get_last_element_from_context_list()

    if element:

        messages.append('If you want more information, I can tell you:')
        btn.get_buttons_element_relations(buttons, element['element_name'])

    else:
        msg_simple.EMPTY_CONTEXT_LIST(messages)


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
    pos = extract_entities(entities, nlu.ENTITY_POSITION)[0]['value']

    if pos:
        position = int(pos[:-2])

        # if context is not empty
        if context.get_action_name_list():

            if position == nlu.VALUE_POSITION_RESET_CONTEXT:
                context.reset_context_list()
                msg_simple.CONTEXT_LIST_RESET(messages)

            elif position - 1 < len(context.get_action_name_list()):
                context.go_back_to_position(position)
                view_context_element(entities, messages, buttons)

            else:
                # todo the selection is wrong, maybe create a message for this
                action_show_context(entities, messages, buttons)
        else:
            msg_simple.EMPTY_CONTEXT_LIST(messages)

    else:
        action_show_context(entities, messages, buttons)


# EXECUTION

intents_to_action_functions = {
    nlu.INTENT_FIND_ELEMENT_BY_ATTRIBUTE: action_find_element_by_attribute,
    nlu.INTENT_CROSS_RELATION: action_cross_relation,
    nlu.INTENT_SHOW_RELATIONS: action_show_relations,
    nlu.INTENT_SHOW_MORE: action_show_more,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position,
    nlu.INTENT_SHOW_CONTEXT: action_show_context
}


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
