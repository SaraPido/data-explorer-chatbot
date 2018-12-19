from modules.patterns import nlu
from modules.database import resolver


def get_buttons_element_relations(element_name):
    relations = resolver.get_element_properties(element_name)['relations']
    buttons = []
    for with_el, by_list in relations.items():
        if by_list:
            for by_el in by_list:
                title = '{} -> {}'.format(by_el, with_el)
                payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                          [nlu.ENTITY_ELEMENT_NAME, with_el],
                                          [nlu.ENTITY_BY_ELEMENT_NAME, by_el])
                buttons.append({'title': title, 'payload': payload})
        else:
            title = with_el
            payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                      [nlu.ENTITY_ELEMENT_NAME, with_el])
            buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_select_element(element_name, element_list):
    word_column_list = resolver.get_element_properties(element_name)['word_column_list']
    buttons = []
    for i, e in enumerate(element_list):
        title = ' '.join(e[x] for x in word_column_list)
        payload = extract_payload(nlu.INTENT_SELECT_ELEMENT_BY_POSITION,
                                  [nlu.ENTITY_POSITION, i + 1])
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_view_related_element(element_name, related_element_name):
    pass


'''
def get_buttons_word_column_list(element_type, element_list, payload_list):
    word_column_list = resolver.get_element_properties(element_type)['word_column_list']
    buttons = []
    for i, e in enumerate(element_list):
        title = ' '.join(e[x] for x in word_column_list)
        payload = payload_list[i]
        buttons.append({'title': title, 'payload': payload})
    return buttons
'''


def get_buttons_go_back_to_context_position(action_name_and_position_list):
    buttons = []
    payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                              [nlu.ENTITY_POSITION, nlu.VALUE_POSITION_RESET_CONTEXT])
    buttons.append({'title': 'RESET context ', 'payload': payload})

    for action_name, position in action_name_and_position_list:
        title = action_name
        payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                                  [nlu.ENTITY_POSITION, position])
        buttons.append({'title': title, 'payload': payload})
    return buttons

# helper


def extract_payload(intent_name, *entity_pairs):
    payload = '/{}'.format(intent_name)
    entities = ', '.join('"{}":"{}"'.format(ep[0], ep[1]) for ep in entity_pairs)
    if entities:
        payload += '{' + entities + '}'
    return payload
