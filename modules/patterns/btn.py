from modules.patterns import nlu
from modules.database import resolver


def get_buttons_element_relations(buttons, element_name):
    relations = resolver.extract_relations(element_name)
    for rel in relations:
        title = rel['keyword']
        # todo payload for join
        payload = '/show_context'#extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                   #               [nlu.ENTITY_RELATED_ELEMENT_NAME, with_el])
        buttons.append({'title': title, 'payload': payload})


def get_buttons_select_element(buttons, element):
    show_columns = resolver.extract_show_columns(element['element_name'])
    for i, e in enumerate(element['value']):
        title = ' '.join(e[x] for x in show_columns)
        payload = extract_payload(nlu.INTENT_SELECT_ELEMENT_BY_POSITION,
                                  [nlu.ENTITY_POSITION, str(i+1)+'xx'])
        buttons.append({'title': title, 'payload': payload})


def get_buttons_view_related_element_by_pos(buttons, element, related_element_name, by_element_name=None):
    show_column_list = resolver.get_element_properties(element['element_name'])['show_column_list']
    for i, e in enumerate(element['value']):
        if by_element_name:
            title = ' '.join(str(e[x]) for x in show_column_list)
            payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                      [nlu.ENTITY_RELATED_ELEMENT_NAME, related_element_name],
                                      [nlu.ENTITY_BY_ELEMENT_NAME, by_element_name],
                                      [nlu.ENTITY_POSITION, str(i+1)+'xx'])
        else:
            title = ' '.join(str(e[x]) for x in show_column_list)
            payload = extract_payload(nlu.INTENT_VIEW_RELATED_ELEMENT,
                                      [nlu.ENTITY_RELATED_ELEMENT_NAME, related_element_name],
                                      [nlu.ENTITY_POSITION, str(i+1)+'xx'])
        buttons.append({'title': title, 'payload': payload})


def get_buttons_go_back_to_context_position(buttons, action_name_list):
    payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                              [nlu.ENTITY_POSITION, str(nlu.VALUE_POSITION_RESET_CONTEXT)+'xx'])
    buttons.insert(0, {'title': 'RESET context ', 'payload': payload})
    for i, action_name in enumerate(action_name_list):
        title = action_name
        payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                                  [nlu.ENTITY_POSITION, str(i+1)+'xx'])  # position plus 1 + xx (st, nd, rd, th)
        # prepending
        buttons.insert(0, {'title': title, 'payload': payload})

# helper


def extract_payload(intent_name, *entity_pairs):
    payload = '/{}'.format(intent_name)
    entities = ','.join('"{}":"{}"'.format(ep[0], ep[1]) for ep in entity_pairs)
    if entities:
        payload += '{' + entities + '}'
    return payload
