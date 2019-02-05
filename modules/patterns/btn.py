from modules.patterns import nlu
from modules.database import resolver


def get_start_buttons():
    return [{'title': 'Find customers located in Milan', 'payload': 'find customer located in Milan'},
            {'title': 'Find employees that work in Paris', 'payload': 'find employees that work in Paris'},
            {'title': 'Again?', 'payload': '/start'}]


def get_buttons_element_relations(element_name):
    relations = resolver.extract_relations(element_name)
    buttons = []
    for rel in relations:
        title = rel['keyword']
        payload = extract_payload(nlu.INTENT_CROSS_RELATION,
                                 [nlu.ENTITY_RELATION, rel['keyword']])
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_select_element(element):
    buttons = []
    show_columns = resolver.extract_show_columns(element['element_name'])
    for i in range(element['show']['from'], element['show']['to']):
        title = ''
        for sh in show_columns:
            title += sh['keyword'] + ': ' if sh.get('keyword') else ''
            title += ' '.join(str(element['value'][i][x]) for x in sh['columns'])

        title = ', '.join((sh['keyword'] + ': ' if sh.get('keyword') else '')
                          + ' '.join(str(element['value'][i][x]) for x in sh['columns'])
                          for sh in show_columns)
        payload = extract_payload(nlu.INTENT_SELECT_ELEMENT_BY_POSITION,
                                  [nlu.ENTITY_POSITION, str(i+1)+'xx'])  # the action removes the first 2 letters
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_button_show_more():
    title = '- SHOW MORE -'
    payload = extract_payload(nlu.INTENT_SHOW_MORE)
    return {'title': title, 'payload': payload}


def get_buttons_go_back_to_context_position(action_name_list):
    payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                              [nlu.ENTITY_POSITION, str(nlu.VALUE_POSITION_RESET_CONTEXT)+'xx'])
    buttons = []
    buttons.insert(0, {'title': 'RESET context ', 'payload': payload})
    for i, action_name in enumerate(action_name_list):
        title = action_name
        payload = extract_payload(nlu.INTENT_GO_BACK_TO_CONTEXT_POSITION,
                                  [nlu.ENTITY_POSITION, str(i+1)+'xx'])  # position plus 1 + xx (st, nd, rd, th)
        # prepending
        buttons.insert(0, {'title': title, 'payload': payload})
    return buttons


# helper

def extract_payload(intent_name, *entity_pairs):
    payload = '/{}'.format(intent_name)
    entities = ','.join('"{}":"{}"'.format(ep[0], ep[1]) for ep in entity_pairs)
    if entities:
        payload += '{' + entities + '}'
    return payload
