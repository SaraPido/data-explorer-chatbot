import copy
import logging
import re

from modules import commons
from modules.database import resolver
from modules import patterns
from modules.patterns import btn, msg, nlu
from modules.settings import ELEMENT_VISU_LIMIT, CONTEXT_VISU_LIMIT, ELEMENT_SIMILARITY_DISTANCE_THRESHOLD

logger = logging.getLogger(__name__)


# ENTITIES EXTRACTORS

def extract_entities(entities, entity_name):
    found = []
    for e in entities:
        if e.get('entity').startswith(entity_name):  # TODO, I made a little trick here...
            found.append(e)
    return found


def extract_single_entity_value(entities, entity_name):
    found = extract_entities(entities, entity_name)
    if found:
        return found[0]['value']  # the first one
    return None


def compute_ordered_entity_list(entities):
    ordered_entities = []

    for e in entities[::-1]:

        ty = None
        op = '='  # the control of the presence of the OP is made here!
        match = re.match("(\w+)_\d_(\d)", e['entity'])
        if match:
            what = match.group(1)
            if what == nlu.ENTITY_WORD:
                ty = 'word'
                maybe_op = next((a['value'] for a in entities if a['entity'].startswith('op_word')), None)
                if maybe_op and maybe_op.endswith('ne'):
                    op = '<>'
                else:
                    op = 'LIKE'  # TODO: here forcing the "word" to be LIKE and not equal, in case
            elif what == nlu.ENTITY_NUMBER:
                ty = 'num'
                maybe_op = next((a['value'] for a in entities if a['entity'].startswith('op_num')), None)
                if maybe_op:
                    if maybe_op.endswith('lt'):
                        op = '<'
                    elif maybe_op.endswith('eq'):
                        op = '='
                    elif maybe_op.endswith('gt'):
                        op = '>'

        if ty:
            oe = {'type': ty, 'op': op, 'value': e['value']}
            attr = next((a['value'] for a in entities if re.match("attr_\d_\d", a['entity'])), None)
            if attr:
                oe['attribute'] = attr
            ordered_entities.append(oe)

    print(ordered_entities)
    return ordered_entities


# ATTRIBUTES HANDLERS

def get_attributes_from_ordered_entities(element_name, ordered_entities):
    attributes = []

    for oe in ordered_entities:

        # todo it gave error: Generate error in case of not-extracted element
        # if the entity has an attribute, i.e. if it not implied
        if oe.get('attribute'):
            keyword_list = [a['keyword'] for a in resolver.extract_attributes_with_keyword(element_name)]
            attribute_name = commons.extract_similar_value(oe['attribute'],
                                                           keyword_list,
                                                           ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)

            if attribute_name:
                attr = resolver.get_attribute_by_name(element_name, attribute_name)
                if attr.get('type') == oe.get('type'):
                    attr['value'] = oe.get('value')
                    attr['op'] = oe.get('op', '=')  # should not happen
                    attributes.append(attr)

            else:  # if it has an attribute but is not recognized
                return []  # something unwanted just happened -> attribute extracted but not matched

        # if the entity does not have an attribute
        else:
            attr = resolver.get_attribute_without_keyword_by_type(element_name, oe.get('type'))
            if attr:
                attr['value'] = oe.get('value')
                attr['op'] = oe.get('op', '=')
                attributes.append(attr)

    return attributes


# SIMILARITY HANDLERS

def handle_element_name_similarity(element_name_received):
    all_elements_names = resolver.get_all_primary_element_names_and_aliases()
    similar = commons.extract_similar_value(element_name_received,
                                            all_elements_names,
                                            ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)
    if similar:
        return resolver.get_element_name_from_possible_alias(similar)
    return None


def handle_element_relations_similarity(element_name, relation_name_received):
    relations = resolver.extract_relations(element_name)
    all_relations_names = [r['keyword'] for r in relations]
    return commons.extract_similar_value(relation_name_received,
                                         all_relations_names,
                                         ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)


# RESPONSE HANDLERS

def handle_response_for_quantity_found_element(response, element):
    if element['real_value_length'] == 1:
        response.add_message(msg.ONE_RESULT_FOUND)
    else:
        response.add_message(msg.N_RESULTS_FOUND_PATTERN.format(element['real_value_length']))


# SELECTION HANDLERS

def is_selection_valid(element, position):
    return 0 < position <= len(element['value'])  # element['real_value_length']:


def add_selected_element_to_context(element, position, context):
    # copying the dictionary
    selected_element = dict(element)

    # I must save it as a list
    selected_element['value'] = [element['value'][position - 1]]

    selected_element['query'] = None
    selected_element['real_value_length'] = 1
    selected_element['action_name'] = '..selected from:'

    context.append_element(selected_element)


# ACTIONS

def action_start(entities, response, context):
    response.add_message(msg.HI_THERE)
    response.add_buttons(btn.get_start_buttons())


def action_find_element_by_attribute(entities, response, context):
    element_name = handle_element_name_similarity(extract_single_entity_value(entities, nlu.ENTITY_ELEMENT))
    ordered_entities = compute_ordered_entity_list(entities)

    if element_name and ordered_entities:
        attributes = get_attributes_from_ordered_entities(element_name, ordered_entities)
        if attributes:
            element = resolver.query_find(element_name, attributes)
            if element['value']:
                element['action_name'] = '...found with attribute(s) "{}".'.format(', '.join(
                    ('{} '.format(a.get('keyword')) if a.get('keyword') else '') + str(a['value']) for a in attributes))
                context.append_element(element)
                handle_response_for_quantity_found_element(response, element)
                action_view_context_element(entities, response, context)

            else:
                response.add_message(msg.NOTHING_FOUND)
        else:
            response.add_message(msg.ERROR)

    else:
        response.add_message(msg.ERROR)


def action_filter_element_by_attribute(entities, response, context):
    element = context.get_last_element()

    if element:

        if element['real_value_length'] > 1:
            ordered_entities = compute_ordered_entity_list(entities)
            attributes = get_attributes_from_ordered_entities(element['element_name'], ordered_entities)

            if attributes:
                all_attributes = copy.deepcopy(attributes)
                # here down union of attributes
                all_attributes += copy.deepcopy(element['attributes']) if element.get('attributes') else []
                result_element = resolver.query_find(element['element_name'], all_attributes)

                if result_element['value']:
                    result_element['action_name'] = '...by filtering with attribute(s) "{}":'.format(', '.join(
                        ('{} '.format(a.get('keyword')) if a.get('keyword') else '') + str(a['value']) for a in
                        attributes))
                    context.append_element(result_element)
                    handle_response_for_quantity_found_element(response, result_element)
                    action_view_context_element(entities, response, context)

                else:
                    response.add_message(msg.NOTHING_FOUND)

            else:
                response.add_message(msg.ERROR)

        else:
            response.add_message('Filtering is not possible now...')

    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_cross_relation(entities, response, context):
    element = context.get_last_element()

    # todo handle case no element is extracted
    extracted_relation_name = extract_entities(entities, nlu.ENTITY_RELATION)[0]['value']
    relation_name = handle_element_relations_similarity(element['element_name'], extracted_relation_name)

    if element and relation_name:

        # control if there is ONLY an element in context_list
        if element['real_value_length'] == 1:

            result_element = resolver.query_join(element, relation_name)

            if result_element['value']:

                result_element['action_name'] = '...reached with the relation "{}", from {}:' \
                    .format(relation_name, element['element_name'])

                context.append_element(result_element)

                handle_response_for_quantity_found_element(response, result_element)

                action_view_context_element(entities, response, context)

            else:
                response.add_message(msg.NOTHING_FOUND)


def action_show_relations(entities, response, context):
    element = context.get_last_element()
    if element:
        response.add_message('If you want more information, I can tell you:')
        response.add_buttons(btn.get_buttons_element_relations(element['element_name']))
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_select_element_by_position(entities, response, context):
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)

    if pos:
        # attention, I suppose "position" is in the form "1st", "2nd", ...
        position = int(pos[:-2])

        element = context.get_last_element()

        if element:

            if element['real_value_length'] == 1:
                response.add_message('There is only one element!\n')
                action_view_context_element(entities, response, context)

            else:
                if is_selection_valid(element, position):
                    add_selected_element_to_context(element, position, context)
                    action_view_context_element(entities, response, context)
                else:
                    response.add_message('Error! Out of range selection!')

        else:
            response.add_message(msg.EMPTY_CONTEXT_LIST)

    else:
        response.add_message(msg.ERROR)


def action_view_context_element(entities, response, context):
    element = context.view_last_element()

    if element:
        if element['real_value_length'] == 1:
            response.add_message(msg.INTRODUCE_ELEMENT_TO_SHOW_PATTERN.format(element['element_name']))
            response.add_message(msg.element_attributes(element))
            action_show_relations(entities, response, context)
        else:
            if element['show']['from'] == 0:
                response.add_message(msg.SELECT_FOR_INFO)
            response.add_message('Shown results from {} to {} of {}'.format(element['show']['from'] + 1,
                                                                            element['show']['to'],
                                                                            element['real_value_length']))
            response.add_buttons(btn.get_buttons_select_element(element))
            if element['show']['to'] < element['real_value_length']:
                response.add_button(btn.get_button_show_more_element())
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_show_more_elements(entities, response, context):
    element = context.get_last_element()

    if element and element['real_value_length'] > 1:
        if element['show']['to'] < element['real_value_length']:
            element['show']['from'] = element['show']['from'] + ELEMENT_VISU_LIMIT
            element['show']['to'] = min(element['real_value_length'], element['show']['to'] + ELEMENT_VISU_LIMIT)
            context.reset_show_last_element = False
            action_view_context_element(entities, response, context)
        else:
            response.add_message(msg.ERROR)  # should not happen
    else:
        response.add_message(msg.ERROR)


def action_show_context(entities, response, context):
    context_list = context.view_context_list()  # _to_show()

    if context_list:

        from_v = context.context_list_indices['from']
        to_v = context.context_list_indices['to']

        for i, el in enumerate(context_list[from_v:to_v][::-1]):

            if el['real_value_length'] == 1:
                result = '{}'.format(resolver.get_element_show_string(el['element_name'], el['value'][0]))
            else:
                result = 'a list of type "{}"'.format(el['element_name'])

            if to_v == len(context_list) and not i:  # the very first one
                response.add_message(msg.SHOW_CONTEXT_INFO)
                m = 'Currently you are viewing'
                m += ' {}:'.format(context_list[-1]['element_name']) \
                    if context_list[-1]['real_value_length'] == 1 else ':'
                response.add_message(m)
                response.add_button(btn.get_button_view_context_element(result))
            else:
                if not i:  # the first ones, in a "show more" list
                    # adding the last action name of the previous "set" of actions
                    response.add_message(context_list[to_v]['action_name'])
                response.add_button(btn.get_button_go_back_to_context_position(result, len(context_list) - i - 1))

            if i != to_v - from_v - 1 or not from_v:
                response.add_message(el['action_name'])

        if from_v:
            response.add_button(btn.get_button_show_more_context())
        else:
            response.add_button(btn.get_button_reset_context())

    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_show_more_context(entities, response, context):
    context_list = context.get_context_list()

    if context_list:
        if context.context_list_indices['from']:  # if it is not 0
            context.context_list_indices['from'] = max(context.context_list_indices['from'] - CONTEXT_VISU_LIMIT, 0)
            context.context_list_indices['to'] = context.context_list_indices['to'] - CONTEXT_VISU_LIMIT
            context.reset_show_context_list = False
            action_show_context(entities, response, context)
        else:
            response.add_message(msg.ERROR)  # should not happen
    else:
        response.add_message(msg.ERROR)  # should not happen


def action_go_back_to_context_position(entities, response, context):
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)

    if pos:
        position = int(pos[:-2])

        # if context is not empty
        if context.get_context_list():

            if position == nlu.VALUE_POSITION_RESET_CONTEXT:
                context.reset_context_list()
                response.add_message(msg.CONTEXT_LIST_RESET)

            elif position - 1 < len(context.get_context_list()):
                context.go_back_to_position(position)
                response.add_message('Ok, now resuming your history... DONE!')
                action_view_context_element(entities, response, context)

            else:
                # todo the selection is wrong, maybe create a message for this
                action_show_context(entities, response, context)
        else:
            response.add_message(msg.EMPTY_CONTEXT_LIST)

    else:
        action_show_context(entities, response, context)


# EXECUTION

intents_to_action_functions = {
    nlu.INTENT_START: action_start,
    nlu.INTENT_FIND_ELEMENT_BY_ATTRIBUTE: action_find_element_by_attribute,
    nlu.INTENT_FILTER_ELEMENT_BY_ATTRIBUTE: action_filter_element_by_attribute,
    nlu.INTENT_CROSS_RELATION: action_cross_relation,
    nlu.INTENT_SHOW_RELATIONS: action_show_relations,
    nlu.INTENT_SHOW_MORE_ELEMENTS: action_show_more_elements,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position,
    nlu.VIEW_CONTEXT_ELEMENT: action_view_context_element,
    nlu.INTENT_SHOW_CONTEXT: action_show_context,
    nlu.INTENT_SHOW_MORE_CONTEXT: action_show_more_context,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position
}


def execute_action_from_intent_name(intent_name, entities, context):
    response = patterns.Response()
    action_function = intents_to_action_functions.get(intent_name)
    if action_function:
        action_function(entities, response, context)
    else:
        response.add_message(msg.ERROR)
    return response
