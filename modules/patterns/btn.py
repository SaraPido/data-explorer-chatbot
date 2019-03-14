from modules.patterns import nlu
from modules.database import resolver


def get_buttons_element_relations(element_name):
    relations = resolver.extract_relations(element_name)
    buttons = []
    for rel in relations:
        title = rel['keyword']
        payload = extract_payload(nlu.INTENT_CROSS_RELATION,
                                 [nlu.ENTITY_RELATION, rel['keyword']])
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_button_filter_hints():
    return {'title': 'FILTER HINTS', 'payload': extract_payload(nlu.INTENT_MORE_INFO_FILTER)}


def get_buttons_select_element(element):
    buttons = []
    for i in range(element['show']['from'], element['show']['to']):
        title = resolver.get_element_show_string(element['element_name'], element['value'][i])
        payload = extract_payload(nlu.INTENT_SELECT_ELEMENT_BY_POSITION,
                                  [nlu.ENTITY_POSITION, str(i+1)])
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_button_show_more_element():
    title = '- SHOW MORE -'
    payload = extract_payload(nlu.INTENT_SHOW_MORE_ELEMENTS)
    return {'title': title, 'payload': payload}


def get_button_show_more_context():
    title = '- SHOW MORE HISTORY -'
    payload = extract_payload(nlu.INTENT_SHOW_MORE_CONTEXT)
    return {'title': title, 'payload': payload}


def get_button_view_context_element(title):
    payload = extract_payload(nlu.VIEW_CONTEXT_ELEMENT)
    return {'title': title, 'payload': payload}


def get_button_reset_context():
    payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                              [nlu.ENTITY_POSITION, str(nlu.VALUE_POSITION_RESET_CONTEXT)])
    return {'title': '- RESET HISTORY -', 'payload': payload}


def get_button_go_back_to_context_position(action_name, pos):
    title = action_name
    payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                              [nlu.ENTITY_POSITION, str(pos)])
    return {'title': title, 'payload': payload}


def get_buttons_help():
    buttons = [{'title': 'Help on ELEMENTS', 'payload': extract_payload(nlu.INTENT_HELP_ELEMENTS)},
               {'title': 'Help on HISTORY', 'payload': extract_payload(nlu.INTENT_HELP_HISTORY)},
               {'title': 'Help on GOING BACK', 'payload': extract_payload(nlu.INTENT_HELP_GO_BACK)}]
    return buttons


# helper

def extract_payload(intent_name, *entity_pairs):
    payload = '/{}'.format(intent_name)
    entities = ','.join('"{}":"{}"'.format(ep[0], ep[1]) for ep in entity_pairs)
    if entities:
        payload += '{' + entities + '}'
    return payload
