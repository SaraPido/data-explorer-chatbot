import copy
import logging
import re
from pprint import pprint

from modules import commons
from modules.database import resolver
from modules import patterns
from modules.patterns import btn, msg, nlu
from settings import ELEMENT_VISU_LIMIT, CONTEXT_VISU_LIMIT, ELEMENT_SIMILARITY_DISTANCE_THRESHOLD

logger = logging.getLogger(__name__)


# ENTITIES EXTRACTORS

def extract_entities(entities, entity_name):
    found = []
    for e in entities:
        if e.get('entity').startswith(entity_name):  # el_1 -> el, word_2_4 -> word
            found.append(e)
    return found


def extract_single_entity_value(entities, entity_name):
    found = extract_entities(entities, entity_name)
    if found:
        return found[0]['value']  # the first one
    return None


def compute_ordered_entity_list(entities):
    print('\ncompute_ordered_entity_list', entities)
    ordered_entities = []

    index_previous_attribute = None
    index_previous_entity_number_op = None

    #for e in entities[::-1]:
    for index, e in enumerate(entities):
        print('index, e ', index, e)
        ty = None
        op = '='  # the control of the presence of the OP is made here!
        #match = re.match("(\w+)_\d_(\d)", e['entity'])
        match = re.match("(\w+)_\d+_(\d+)|el_(columns)", e['entity'])
        print('match ', match)
        if re.match("attr_\d+_\d+_\d+", entities[index - 1]['entity']):
            index_previous_attribute = entities[index - 1]
        elif entities[index - 1]['entity'].startswith('op_num'):
            index_previous_entity_number_op = entities[index - 1]
        if match:
            what = match.group(1)
            if what == nlu.ENTITY_WORD:
                ty = 'word'
                maybe_op = next((a['value'] for a in entities if a['entity'].startswith('op_word')), None)
                if maybe_op and maybe_op.endswith('ne'):
                    op = '<>'
                else:
                    op = 'LIKE'  # here forcing the attribute of type "word" to be LIKE and NOT equal
            elif what == nlu.ENTITY_NUMBER:
                ty = 'num'
                #maybe_op = next((a['value'] for a in entities if a['entity'].startswith('op_num')), None)
                #maybe_op = commons.extract_similar_value(maybe_op, ['less than', 'more than'], 6)

                if index_previous_entity_number_op:
                    maybe_op = index_previous_entity_number_op['value']
                else:
                    maybe_op = None
                maybe_op = commons.extract_similar_value(maybe_op, ['less than', 'more than'], 6)

                if maybe_op:
                    if maybe_op == 'less than':
                        op = '<'
                    elif maybe_op == 'more than':
                        op = '>'
                else:
                    op = '='

            elif what == nlu.ENTITY_COLUMNS:
                ty = 'columns'
                op = 'ORDER BY'

        if ty:
            oe = {'type': ty, 'operator': op, 'value': e['value']}
            for index2, e2 in enumerate(entities):
                if index2 == index+1:
                    if e2['entity'] == 'or':
                        oe['and_or'] = 'or'
                    elif re.match('attr_\d+_\d+_\d+',e2['entity']) or e2['entity'] == 'and':
                        oe['and_or'] = 'and'
            if ty == 'columns':
                attr = next((a['value'] for a in entities if re.match("order_by", a['entity'])), None)
            else:
                if index_previous_attribute:
                    attr = index_previous_attribute['value']
                else:
                    attr = None

            attr = next((a['value'] for a in entities if re.match("attr_\d+_\d+_\d+", a['entity'])), None)
            if attr:
                oe['attribute'] = attr
            ordered_entities.append(oe)
    print('\ncompute_ordered_entity_list ', ordered_entities)
    return ordered_entities


# ATTRIBUTES HANDLERS

def get_attributes_from_ordered_entities(element_name, ordered_entities, response):
    print('get_attributes_from_ordered_entities ', element_name, ordered_entities, response)
    attributes = []

    for oe in ordered_entities:
        # if the entity has an attribute, i.e. if it not implied
        if oe.get('attribute'):
            order_by_alias = ['order by', 'ordered by', 'sort by', 'sorted by']
            keyword_list = [a['keyword'] for a in resolver.extract_attributes_with_keyword(element_name)]
            print('keyword_list ', keyword_list)
            attribute_name = commons.extract_similar_value(oe['attribute'],
                                                           keyword_list,
                                                           ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)
            for alias in order_by_alias:
                keyword_list.append(alias)
            if attribute_name:
                #attr = resolver.get_attribute_by_name(element_name, attribute_name)
                #if attr.get('type') == oe.get('type'):
                #    attr['value'] = oe.get('value')
                #    attr['operator'] = oe.get('operator', '=')  # should not happen
                #    attributes.append(attr)
                new_attr = resolver.get_attribute_by_name(element_name, attribute_name)
                print('new_attr', new_attr)
                if new_attr:
                    attr = new_attr.copy()
                else:
                    attr = None
                if attr == None and attribute_name in order_by_alias:
                    columns = oe['value']
                    columns_element = handle_columns_name_similarity(element_name, columns)
                    if columns_element:
                        oe['value'] = columns_element
                        attr = {'columns': [columns_element], 'keyword': 'order by', 'operator': 'ORDER BY',
                                'type': 'columns', 'value': columns_element}
                    else:
                        response.add_message('Sorry, there is no attribute "' + columns + '" for ' + element_name)
                        return []
                if attr.get('type') == oe.get('type'):
                    attr['value'] = oe.get('value')
                    if 'and_or' in oe:
                        attr['and_or'] = oe.get('and_or')
                    attr['operator'] = oe.get('operator', '=')  # should not happen
                    attributes.append(attr)
            else:  # if it has an attribute but is not recognized
                return []  # something unwanted just happened -> attribute extracted but not matched

        # if the entity does not have an attribute
        else:
            #attr = resolver.get_attribute_without_keyword_by_type(element_name, oe.get('type'))
            #if attr:
            #    attr['value'] = oe.get('value')
            #    attr['operator'] = oe.get('operator', '=')
           #     attributes.append(attr)
            new_attr = resolver.get_attribute_without_keyword_by_type(element_name, oe.get('type'))
            if new_attr:
                attr = new_attr.copy()
                attr['value'] = oe.get('value')
                if 'and_or' in oe:
                    attr['and_or'] = oe.get('and_or')
                attr['operator'] = oe.get('operator', '=')
                attributes.append(attr)
    print('\nget_attributes_from_ordered_entities ', attributes)
    return attributes

def handle_columns_name_similarity(element_name_alias, columns_name_received):
    displayable_attributes = resolver.simulate_view(element_name_alias)
    attribute_names = [i['attribute'] for i in displayable_attributes if 'attribute' in i]
    similar = commons.extract_similar_value(columns_name_received, attribute_names, ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)
    if similar:
        return similar
    else:
        similar = commons.extract_similar_value(columns_name_received, attribute_names, ELEMENT_SIMILARITY_DISTANCE_THRESHOLD)
        if similar:
            for i in attribute_names:
                if i['display'] is similar:
                    return i['attribute']
        else:
            return None

def get_attributes_string(attributes):
    return ', '.join(('{} '.format(a.get('keyword')) if a.get('keyword') else '')
                              + ('{} '.format(a.get('operator')) if a.get('type') == 'num' else '')
                              + str(a['value']) for a in attributes)


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

def handle_response_for_quantity_found_element(response, element, context):
    if element['real_value_length'] == 1:
        response.add_message(msg.ONE_RESULT_FOUND)
    else:
        response.add_message(msg.N_RESULTS_FOUND_PATTERN.format(element['real_value_length']))
        if element.get('action_type') != 'filter' and \
                element.get('element_name') in resolver.get_all_primary_element_names():
            response.add_message(msg.REMEMBER_FILTER)
            response.add_button(btn.get_button_filter_hints())


# SELECTION HANDLERS

def is_selection_valid(element, position):
    return 0 < position <= len(element['value'])  # element['real_value_length']:


# SOSTITUITA CON METODO IN CONTEXT ADD_SELECTED_ELEMENT
# def add_selected_element_to_context(element, position, context):
#     print('add_selected_element_to_context ', element, position, context)
#     # copying the dictionary
#     print(type(element))
#     if type(element) is dict:
#         selected_element = element#dict(element)
#     else:
#         selected_element = {}
#     print('selected_element ', selected_element)
#     # I must save it as a list
#     if 'value' in element:
#         selected_element['value'] = [element['value'][position - 1]]
#     else:
#         selected_element['value'] = element
#     selected_element['query'] = None
#     selected_element['real_value_length'] = 1
#     selected_element['action_name'] = '..selected from:'
#     selected_element['action_type'] = 'select'
#     print('selected_element ', selected_element)
#     context.append_element(selected_element)
#     print('context ', context)

# ACTIONS

def action_start(entities, response, context, add = True):
    print('action_start', entities, response, context, add)
    start_message = msg.HI_THERE + "\n" + msg.element_names_examples()
    response.add_message(start_message)
    #response.add_button(btn.get_buttons_help())
    response.add_buttons(btn.get_buttons_tell_me_more())
    print('added message and button')
    #response.add_buttons(btn.get_buttons_tell_me_more())
    #response.add_message(msg.HI_THERE)
    #response.add_buttons(btn.get_buttons_help())
    if add:
        context.add_selected_element("start", entities)
    else:
        response.add_button(btn.get_button_help_on_elements())
        response.add_button(btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
        response.add_button(btn.get_button_history())
    print('finish')

def action_help_elements(entities, response, context):
    response.add_message(msg.element_names_examples())
    response.add_message(msg.element_names_info_examples())
    #response.add_buttons(btn.get_buttons_help())


def action_help_history(entities, response, context):
    response.add_message(msg.REMEMBER_HISTORY)
    #response.add_button(btn.get_button_help_on_elements())


def action_help_go_back(entities, response, context):
    response.add_message(msg.REMEMBER_GO_BACK)
    #response.add_button(btn.get_button_help_on_elements())


def action_more_info_find(entities, response, context):
    element_name = handle_element_name_similarity(extract_single_entity_value(entities, nlu.ENTITY_ELEMENT))
    if element_name:
        response.add_message(msg.find_element_examples(element_name))
        #response.add_button(btn.get_button_show_more_examples(element_name))
    else:
        response.add_message('I am sorry, I understood that you want more info, but not on what...')
        response.add_message(msg.element_names_info_examples())
    #response.add_button(btn.get_button_help_on_elements())
    # response.add_message('Remember that you can always go back, just click the button')
    #response.add_button(btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
    #response.add_button(btn.get_button_history())


def action_more_info_filter(entities, response, context):
    element_name = handle_element_name_similarity(extract_single_entity_value(entities, nlu.ENTITY_ELEMENT))
    if element_name:
        response.add_message(msg.filter_element_examples(element_name))
    else:
        element = context.get_last_element()
        if element and element['real_value_length'] > 1:
            response.add_message(msg.filter_element_examples(element['element_name']))
        else:
            response.add_message('I am sorry, but there is nothing to filter... You\'d better tell on which element.\n'
                                 'Try, for instance, with "how to filter {}"'
                                 .format(resolver.get_all_primary_element_names()[0]))
    response.add_button(btn.get_button_help_on_elements())
    # response.add_message('Remember that you can always go back, just click the button')
    response.add_button(btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
    response.add_button(btn.get_button_history())

def action_find_element_by_attribute(entities, response, context):
    print('action_find_element_by_attribute ', entities, response, context)
    element_name = handle_element_name_similarity(extract_single_entity_value(entities, nlu.ENTITY_ELEMENT))
    print('element_name ', element_name)
    ordered_entities = compute_ordered_entity_list(entities)
    print('ordered_entities ', ordered_entities)
    if element_name:
        print('element name ', element_name)
        attributes = get_attributes_from_ordered_entities(element_name, ordered_entities, response) if ordered_entities else []
        print('attributes ', attributes)
        if attributes:
            element = resolver.query_find(element_name, attributes)
            print('element ', element)
            if element['value']:
                element['action_name'] = '...found with attribute(s) "{}"'.format(get_attributes_string(attributes))
                element['action_type'] = 'find'
                context.append_element(element)
                handle_response_for_quantity_found_element(response, element, context)
                action_view_context_element(entities, response, context)

            else:
                response.add_message(msg.NOTHING_FOUND)
                response.add_button(btn.get_button_help_on_elements())
                # response.add_message('Remember that you can always go back, just click the button')
                response.add_button(
                    btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
                response.add_button(btn.get_button_history())
        else:
            response.add_message('Ok so you want to find some elements of type {}, but you should '
                                 'tell me something more, otherwise I can\'t help you explore!'.format(element_name))
            response.add_message(msg.find_element_examples(element_name))
            response.add_button(btn.get_button_help_on_elements())
            # response.add_message('Remember that you can always go back, just click the button')
            response.add_button(
                btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
            response.add_button(btn.get_button_history())

    else:
        response.add_message('I guess you want to find something, but I did not understand what!\n')
        response.add_message(msg.element_names_examples())
        response.add_button(btn.get_button_help_on_elements())
        # response.add_message('Remember that you can always go back, just click the button')
        response.add_button(
            btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
        response.add_button(btn.get_button_history())


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
                    result_element['action_name'] = '...by filtering with attribute(s) ' \
                                                    '"{}":'.format(get_attributes_string(attributes))
                    result_element['action_type'] = 'filter'
                    context.append_element(result_element)
                    handle_response_for_quantity_found_element(response, result_element, context)
                    action_view_context_element(entities, response, context)

                else:
                    response.add_message(msg.NOTHING_FOUND)
                    response.add_button(btn.get_button_help_on_elements())
                    # response.add_message('Remember that you can always go back, just click the button')
                    response.add_button(
                        btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
                    response.add_button(btn.get_button_history())

            else:
                response.add_message("I didn't understand for what do you want to filter by\n")
                action_more_info_filter(entities, response, context)

        else:
            response.add_message('Filtering is not possible now, there is only one element under to view!')
            response.add_button(btn.get_button_help_on_elements())
            # response.add_message('Remember that you can always go back, just click the button')
            response.add_button(
                btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
            response.add_button(btn.get_button_history())

    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_cross_relation(entities, response, context):
    element = context.get_last_element()

    if element:

        extracted_relation_name = extract_single_entity_value(entities, nlu.ENTITY_RELATION)
        relation_name = handle_element_relations_similarity(element['element_name'], extracted_relation_name)

        if relation_name:

            # control if there is ONLY an element in context_list
            if element['real_value_length'] == 1:

                result_element = resolver.query_join(element, relation_name)

                if result_element['value']:

                    result_element['action_name'] = '...reached with the relation "{}", from {}:' \
                        .format(relation_name, element['element_name'])
                    result_element['action_type'] = 'cross'

                    context.append_element(result_element)

                    handle_response_for_quantity_found_element(response, result_element, context)

                    action_view_context_element(entities, response, context)

                else:
                    response.add_message(msg.NOTHING_FOUND)
                    response.add_button(btn.get_button_help_on_elements())
                    response.add_button(btn.get_button_view_context_element('- GO BACK TO THE CONCEPT! -'))
                    # response.add_message('Remember that you can always go back, just click the button')
                    response.add_button(btn.get_button_history())

    else:
        response.add_message(msg.ERROR)
        response.add_button(btn.get_button_help_on_elements())


def action_show_relations(entities, response, context):
    print('\naction_show_relations ', entities, response, context)
    element = context.get_last_element()
    print('element ', element)
    if element:

        #buttons = btn.get_buttons_element_relations(element['element_name'])
        response.add_message('If you want more information, I can tell you:')
        response.add_buttons(btn.get_buttons_element_relations(element['element_name']))
        #response.add_buttons(buttons)
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_select_element_by_position(entities, response, context):
    print('\naction_select_element_by_position')
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)
    print('pos ', pos)
    if pos:
        # attention, I suppose "position" is in the form "1st", "2nd", ...
        position = int(pos)

        element = context.get_last_element()
        print('element ', element)
        if element:

            if element['real_value_length'] == 1:
                response.add_message('There is only one element!\n')
                action_view_context_element(entities, response, context)

            else:
                if is_selection_valid(element, position):
                    context.add_selected_element(element, position)
                    action_view_context_element(entities, response, context)
                else:
                    response.add_message('Error! Out of range selection!')
                    response.add_button(btn.get_button_help_on_elements())
                    response.add_button(
                        btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
                    response.add_button(btn.get_button_history())

        else:
            response.add_message(msg.EMPTY_CONTEXT_LIST)
            response.add_button(btn.get_button_help_on_elements())
            response.add_button(
                btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
            response.add_button(btn.get_button_history())

    else:
        response.add_message(msg.ERROR)
        response.add_button(btn.get_button_help_on_elements())
        # response.add_message('Remember that you can always go back, just click the button')
        response.add_button(
            btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
        response.add_button(btn.get_button_history())


def action_view_context_element(entities, response, context):
    print('\naction_view_context_element')
    element = context.view_last_element()
    print('element ', element)
    if element:
        if element['real_value_length'] == 1:
            response.add_message(msg.INTRODUCE_ELEMENT_TO_SHOW_PATTERN.format(element['element_name']))
            response.add_message(msg.element_attributes(element))
            print('entered if element[\'real_value_length\'] == 1')
            if element.get('element_name') not in resolver.get_all_primary_element_names():  # IF OF TYPE SECONDARY
                response.add_message('If you want to go back, just click the following button')
                response.add_button(btn.get_button_go_back_to_context_position('Go back!',
                                                                               len(context.get_context_list()) - 1))
                print('entered element.get(\'element_name\') not in resolver.get_all_primary_element_names()')
            else:
                action_show_relations(entities, response, context)
        else:
            if element['show']['from'] == 0:
                print("\n if element['show']['from'] == 0: \n")
                if element.get('element_name') not in resolver.get_all_primary_element_names():  # IF OF TYPE SECONDARY
                    print("\nif element.get('element_name') not in resolver.get_all_primary_element_names():\n")
                    response.add_message('If you want to go back, just click the following button')
                    response.add_button(btn.get_button_go_back_to_context_position('Go back!',
                                                                                   len(context.get_context_list()) - 1))
                print("element.get('element_name') ", element.get('element_name'))
                response.add_message(msg.SELECT_FOR_INFO_PATTERN.format(element.get('element_name')))
            print("element['show']['from'] + 1 ", element['show']['from'] + 1)
            print("element['show']['to']", element['show']['to'])
            print("element['real_value_length']", element['real_value_length'])
            response.add_message('Shown results from {} to {} of {}'.format(element['show']['from'] + 1,
                                                                            element['show']['to'],
                                                                            element['real_value_length']))

            #  response.add_message(msg.element_list(element))
            response.add_buttons(btn.get_buttons_select_element(element))
            print('added select buttons ')
            if element['show']['to'] < element['real_value_length']:
                print("element['show']['to'] < element['real_value_length']")
                response.add_button(btn.get_button_show_more_element())
            response.add_button(btn.get_button_order_by())
            print('added buttons action select by pos')
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)
    response.add_button(btn.get_button_help_on_elements())
    response.add_button(btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
    response.add_button(btn.get_button_history())
    print('finish  action select by pos\n')


def action_show_more_elements(entities, response, context):
    element = context.get_last_element()

    if element and element['real_value_length'] > 1:
        if element['show']['to'] < element['real_value_length']:
            element['show']['from'] = element['show']['from'] + ELEMENT_VISU_LIMIT
            element['show']['to'] = min(element['real_value_length'], element['show']['to'] + ELEMENT_VISU_LIMIT)
            context.reset_show_last_element = False
            action_view_context_element(entities, response, context)
        else:
            response.add_message('I am sorry, but there is nothing to show more...')
    else:
        response.add_message('I am sorry, but there is nothing to show more...')


def action_show_context(entities, response, context):
    context_list = context.view_context_list()  # _to_show()

    if context_list:

        up = context.context_list_indices['up']
        down = context.context_list_indices['down']

        for i, el in enumerate(context_list[down:up][::-1]):

            if el['real_value_length'] == 1:
                result = '{}'.format(resolver.get_element_show_string(el['element_name'], el['value'][0]))
            else:
                result = 'a list of type "{}"'.format(el['element_name'])

            if up == len(context_list) and i == 0:  # the very first one
                response.add_message(msg.REMEMBER_RESET_HISTORY)
                response.add_button(btn.get_button_reset_context())
                m = 'Currently you are viewing'
                m += ' {}:'.format(context_list[-1]['element_name']) \
                    if context_list[-1]['real_value_length'] == 1 else ':'
                response.add_message(m)
                response.add_button(btn.get_button_view_context_element(result))

            else:
                if i == 0:  # the first ones, in a "show more" list
                    # adding the last action name of the previous "set" of actions
                    response.add_message(context_list[up]['action_name'])
                response.add_button(btn.get_button_go_back_to_context_position(result, up-i))

            if i != up - down - 1 or down == 0 and el['action_type'] == 'find':
                response.add_message(el['action_name'])

        if down != 0:
            response.add_button(btn.get_button_show_more_context())

    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)


def action_show_more_context(entities, response, context):
    context_list = context.get_context_list()

    if context_list:
        if context.context_list_indices['down'] != 0:  # if it is not 0
            context.context_list_indices['down'] = max(context.context_list_indices['down'] - CONTEXT_VISU_LIMIT, 0)
            context.context_list_indices['up'] = context.context_list_indices['up'] - CONTEXT_VISU_LIMIT
            context.reset_show_context_list = False
            action_show_context(entities, response, context)
        else:
            response.add_message('I am sorry, but there is nothing to show more...')
            response.add_button(btn.get_button_help_on_elements())
            # response.add_message('Remember that you can always go back, just click the button')
            response.add_button(
                btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
            response.add_button(btn.get_button_history())
    else:
        response.add_message('I am sorry, but there is nothing to show more...')
        response.add_button(btn.get_button_help_on_elements())
        # response.add_message('Remember that you can always go back, just click the button')
        response.add_button(
            btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
        response.add_button(btn.get_button_history())


def action_go_back_to_context_position(entities, response, context):
    pos = extract_single_entity_value(entities, nlu.ENTITY_POSITION)

    # if context is not empty
    if context.get_context_list():

        length = len(context.get_context_list())

        position = int(pos) if pos else (length - 1)
        # if no position is extracted, set the value to go back only once

        if position == nlu.VALUE_POSITION_RESET_CONTEXT or \
                len(context.get_context_list()) == 1 and position == 0:  # if the list is one el long and no entity pos
            context.reset_context_list()
            response.add_message(msg.CONTEXT_LIST_RESET)

        elif position - 1 < length:
            context.go_back_to_position(position)
            response.add_message('Ok, now resuming your history of {} position{}... DONE!'
                                 .format(length - position, "s" if length - position > 1 else ""))
            action_view_context_element(entities, response, context)

        else:
            # wrong selection
            action_show_context(entities, response, context)
    else:
        response.add_message(msg.EMPTY_CONTEXT_LIST)

def action_order_by(entities, response, context):
    print('action_order_by')
    element = context.get_last_element()
    print('element ', element)
    if element:
        value = element['value']
        element_name = element['element_name']
        value_attributes = value[0] #take first element
        response.add_message('Choose the property you want to order')
        #response.add_button(btn.get_button_help_on_elements())
        response.add_buttons(btn.get_buttons_order_by_attribute(value_attributes,element_name))
    else:
        #response.add_button(btn.get_button_help_on_elements())
        response.add_message('I am sorry, but there is nothing to order...')
    response.add_button(btn.get_button_help_on_elements())
    response.add_button(btn.get_button_history())
    response.add_button(btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))

def action_order_by_attribute(entities, response, context):
    print('action_order_by_attribute')
    attribute_to_order_by = extract_single_entity_value(entities, nlu.ENTITY_POSITION)
    element = context.get_last_element()
    print('attribute ', attribute_to_order_by)
    print('element ', element)
    value = element['value']
    value = sorted(value, key=lambda k: (k[attribute_to_order_by] is None, k[attribute_to_order_by])) # All None element are put in the end
    element['value'] = value
    context.reset_show_last_element = False
    action_view_context_element(entities, response, context)


# EXECUTION

intents_to_action_functions = {
    nlu.INTENT_START: action_start,
    nlu.INTENT_HELP_ELEMENTS: action_help_elements,
    nlu.INTENT_HELP_HISTORY: action_help_history,
    nlu.INTENT_HELP_GO_BACK: action_help_go_back,
    nlu.INTENT_MORE_INFO_FIND: action_more_info_find,
    nlu.INTENT_MORE_INFO_FILTER: action_more_info_filter,
    nlu.INTENT_FIND_ELEMENT_BY_ATTRIBUTE: action_find_element_by_attribute,
    nlu.INTENT_FILTER_ELEMENT_BY_ATTRIBUTE: action_filter_element_by_attribute,
    nlu.INTENT_CROSS_RELATION: action_cross_relation,
    nlu.INTENT_SHOW_RELATIONS: action_show_relations,
    nlu.INTENT_ORDER_BY: action_order_by,
    nlu.INTENT_ORDER_BY_ATTRIBUTE: action_order_by_attribute,
    nlu.INTENT_SHOW_MORE_ELEMENTS: action_show_more_elements,
    nlu.INTENT_SELECT_ELEMENT_BY_POSITION: action_select_element_by_position,
    nlu.VIEW_CONTEXT_ELEMENT: action_view_context_element,
    nlu.INTENT_SHOW_CONTEXT: action_show_context,
    nlu.INTENT_SHOW_MORE_CONTEXT: action_show_more_context,
    nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION: action_go_back_to_context_position
}


def execute_action_from_intent_name(intent_name, entities, context):
    print('execute_action_from_intent_name')
    response = patterns.Response()
    print('response ', response)
    action_function = intents_to_action_functions.get(intent_name)
    print('action_function ', action_function)
    if action_function:
        print('Calling action: {}'.format(action_function.__name__))
        context.log('Calling action: {}'.format(action_function.__name__))
        action_function(entities, response, context)
        print('action function called')
    else:
        print('Executing fallback action')
        context.log('Executing fallback action')
        response.add_message(msg.ERROR)
        response.add_button(btn.get_button_help_on_elements())
        response.add_button(
            btn.get_button_go_back_to_context_position('- GO BACK! -', len(context.get_context_list()) - 1))
        response.add_button(btn.get_button_history())
    print('before response will be')
    context.log('Response will be:\n'
                '\n'
                '{}\n'
                '\n'
                '- - - - - -'.format(response.get_printable_string()))
    print('Response will be:\n'
                '\n'
                '{}\n'
                '\n'
                '- - - - - -'.format(response.get_printable_string()))
    print('response ', response)
    return response
