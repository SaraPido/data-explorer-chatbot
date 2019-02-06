import logging

from nltk import edit_distance
from modules.database import resolver
from modules import context
from modules import patterns
from modules.patterns import btn, msg, nlu

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


def extract_single_entity_value(entities, entity_name):
    found = extract_entities(entities, entity_name)
    if found:
        return found[0]['value']  # the first one
    else:
        return None


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


def handle_show_element(element):
    element['show'] = {'from': 0, 'to': min(LIMIT, element['real_value_length'])}


def handle_quantity_found_element(response, element):
    if element['real_value_length'] == 1:
        response.add_message(msg.ONE_RESULT_FOUND)
    else:
        response.add_message(msg.N_RESULTS_FOUND_PATTERN.format(element['real_value_length']))


def handle_element_selection(element, position):

    if 0 < position <= len(element['value']):  # element['real_value_length']:
        # copying the dictionary
        selected_element = dict(element)

        # I must save it as a list
        selected_element['value'] = [element['value'][position - 1]]

        selected_element['query'] = None
        selected_element['real_value_length'] = 1
        selected_element['action_description'] = 'Selected' + element['element_name'] + \
                                                 ' at position ' + str(position)

        context.append_element(selected_element)
        return True

    return False


def compute_ordered_entity_list(entities):
    ordered_entities = []
    d = {}

    for e in entities[::-1]:  # reverse order

        if e['entity'] == nlu.ENTITY_WORD:
            d = {'type': 'word', 'value': e['value']}
        elif e['entity'] == nlu.ENTITY_NUMBER:
            d = {'type': 'num', 'value': e['value']}
        elif e['entity'] == 'attr' and d:  # nlu.ENTITY_ATTRIBUTE
            a = e['value']
            oe = {'attribute': a}
            oe.update(d)
            ordered_entities.append(oe)

    if not ordered_entities and d:
        ordered_entities.append(d)

    return ordered_entities


# ACTIONS

def action_start(entities, response):
    response.add_message(msg.HI_THERE)
    response.add_buttons(btn.get_start_buttons())


def action_find_element_by_attribute(entities, response):
    element_name = handle_element_name_similarity(extract_single_entity_value(entities, nlu.ENTITY_ELEMENT))
    ordered_entities = compute_ordered_entity_list(entities)

    if element_name and ordered_entities:

        attributes = []

        for oe in ordered_entities:
            if oe.get('attribute'):
                attribute_name = handle_similarity(oe['attribute'],
                                                   [a['keyword']
                                                    for a in resolver.extract_attributes_with_keyword(element_name)])
                if attribute_name:
                    attr = resolver.get_attribute_by_name(element_name, attribute_name)
                    if attr.get('type') == oe.get('type'):
                        attr['value'] = oe.get('value')
                        attributes.append(attr)
            else:
                attr = resolver.get_attribute_without_keyword_by_type(element_name, oe.get('type'))
                if attr:
                    attr['value'] = oe.get('value')
                    attributes.append(attr)

        element = resolver.query_find(element_name, attributes)

        if element['value']:

            handle_show_element(element)

            element['action_description'] = 'TODO for find'

            context.append_element(element)

            handle_quantity_found_element(response, element)

            view_context_element(entities, response, just_appended=True)

        else:
            response.add_message(msg.NOTHING_FOUND)

    else:
        response.add_message(msg.ERROR)


def action_filter_element_by_attribute(entities, response):
    # todo: define its behavior
    pass


def action_cross_relation(entities, response):

    element = context.get_last_element()

    # todo handle case no element is extracted
    extracted_relation_name = extract_entities(entities, nlu.ENTITY_RELATION)[0]['value']
    relation_name = handle_element_relations_similarity(element['element_name'], extracted_relation_name)

    if element and relation_name:

        # control if there is ONLY an element in context_list
        if element['real_value_length'] == 1:

            element = resolver.query_join(element, relation_name)

            if element['value']:
                element['action_description'] = 'TODO for join'

                handle_show_element(element)

                context.append_element(element)

                handle_quantity_found_element(response, element)

                view_context_element(entities, response, just_appended=True)

            else:
                response.add_message(msg.NOTHING_FOUND)


def action_show_relations(entities, response):
    element = context.get_last_element()
    if element:
        response.add_message('If you want more information, I can tell you:')
        response.add_buttons(btn.get_buttons_element_relations(element['element_name']))
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


# SELECT ACTIONS

def action_select_element_by_position(entities, response):
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)

    if pos:
        # attention, I suppose "position" is in the form "1st", "2nd", ...
        position = int(pos[:-2])

        element = context.get_last_element()

        if element:

            if element['real_value_length'] == 1:
                response.add_message('There is only one element!\n')
                view_context_element(entities, response)

            else:
                if handle_element_selection(element, position):
                    handle_show_element(element)
                    view_context_element(entities, response)
                else:
                    response.add_message('Error! Out of range selection!')

        else:
            response.add_message(msg.EMPTY_CONTEXT_LIST)

    else:
        response.add_message(msg.ERROR)


def view_context_element(entities, response, just_appended=False):
    element = context.get_last_element()

    if element:
        if element['real_value_length'] == 1:
            response.add_message(msg.INTRODUCE_ELEMENT_TO_SHOW_PATTERN.format(element['element_name']))
            response.add_message(msg.ELEMENT_ATTRIBUTES_FUNCTION(element))
            action_show_relations(entities, response)
        else:
            if just_appended:
                response.add_message(msg.SELECT_FOR_INFO)
            response.add_message('Shown results from {} to {} of {}'.format(element['show']['from']+1,
                                                                      element['show']['to'],
                                                                      element['real_value_length']))
            response.add_buttons(btn.get_buttons_select_element(element))
            if element['show']['to'] < element['real_value_length']:
                response.add_button(btn.get_button_show_more())
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_show_more(entities, response):
    element = context.get_last_element()

    if element:
        if element['show']['to'] < element['real_value_length']:
            element['show']['from'] = element['show']['from'] + LIMIT
            element['show']['to'] = min(element['real_value_length'], element['show']['to'] + LIMIT)
            view_context_element(entities, response)
        else:
            response.add_message(msg.ERROR)  # should not happen


def action_show_context(entities, response):
    action_name_list = context.get_action_name_list()

    if action_name_list:

        # removing the last element
        action_name = action_name_list.pop()
        response.add_message(msg.SHOW_CONTEXT_INFO)
        response.add_message(msg.SHOW_CURRENT_ACTION_NAME_CONTEXT_PATTERN.format(action_name))
        response.add_buttons(btn.get_buttons_go_back_to_context_position(action_name_list))

    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_go_back_to_context_position(entities, response):
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)

    if pos:
        position = int(pos[:-2])

        # if context is not empty
        if context.get_action_name_list():

            if position == nlu.VALUE_POSITION_RESET_CONTEXT:
                context.reset_context_list()
                response.add_message(msg.CONTEXT_LIST_RESET)

            elif position - 1 < len(context.get_action_name_list()):
                context.go_back_to_position(position)
                view_context_element(entities, response)

            else:
                # todo the selection is wrong, maybe create a message for this
                action_show_context(entities, response)
        else:
            response.add_message(msg.EMPTY_CONTEXT_LIST)

    else:
        action_show_context(entities, response)


# EXECUTION

intents_to_action_functions = {
    nlu.INTENT_START: action_start,
    nlu.INTENT_FIND_ELEMENT_BY_ATTRIBUTE: action_find_element_by_attribute,
    nlu.INTENT_FILTER_ELEMENT_BY_ATTRIBUTE: action_filter_element_by_attribute,
    nlu.INTENT_CROSS_RELATION: action_cross_relation,
    nlu.INTENT_SHOW_RELATIONS: action_show_relations,
    nlu.INTENT_SHOW_MORE: action_show_more,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position,
    nlu.INTENT_SHOW_CONTEXT: action_show_context
}


def execute_action_from_intent_name(intent_name, entities):
    action_function = intents_to_action_functions.get(intent_name)
    if action_function:
        logger.info('Executing action: "' + action_function.__name__ + '"')
        response = patterns.Response()
        action_function(entities, response)
        return response
    else:
        logger.info('Action related to intent "' + intent_name + '" NOT FOUND')
        return execute_fallback()


def execute_fallback():
    # todo review
    response = patterns.Response()
    response.add_message(msg.ERROR)
    logger.info('Executing FALLBACK')
    return response
