from modules.patterns import nlu
from modules.database import resolver


def get_buttons_relation_list(element_type):
    relation_list = resolver.get_element_properties(element_type)['relation_list']
    buttons = []
    for r in relation_list:
        if r['by']:
            for by in r['by']:
                title = '{} {}'.format(by['type'], r['type'])
                payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                          [nlu.ENTITY_ELEMENT_TYPE, r['type']],
                                          [nlu.ENTITY_BY_ELEMENT_TYPE, by['type']])
                buttons.append({'title': title, 'payload': payload})
        else:
            title = r['type']
            payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                      [nlu.ENTITY_ELEMENT_TYPE, r['type']])
            buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_select_element(element_type, element_list):
    word_column_list = resolver.get_element_properties(element_type)['word_column_list']
    buttons = []
    for i, e in enumerate(element_list):
        title = ' '.join(e[x] for x in word_column_list)
        payload = extract_payload(nlu.INTENT_SELECT_ELEMENT_BY_POSITION,
                                  [nlu.ENTITY_POSITION, i + 1])
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_view_related_element(element_type, related_element_type):
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
