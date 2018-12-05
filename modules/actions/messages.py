from modules import database


def get_message_word_list(element_type, element_list):
    word_list = database.get_element_properties(element_type)['word_list']
    message = ''
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in word_list)
        if i != len(element_list) - 1:
            message += '\n'
    return message


def get_message_word_list_with_attribute(element_type, element_list, attribute_type):
    word_list = database.get_element_properties(element_type)['word_list']
    message = ''
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in word_list)
        message += ': ' + str(e[attribute_type])
        if i != len(element_list) - 1:
            message += '\n'
    return message


def get_buttons_word_list(element_type, element_list, payload_list):
    word_list = database.get_element_properties(element_type)['word_list']
    buttons = []
    for i, e in enumerate(element_list):
        title = ' '.join(e[x] for x in word_list)
        payload = payload_list[i]
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_select_element(element_type, element_list):
    word_list = database.get_element_properties(element_type)['word_list']
    buttons = []
    for i, e in enumerate(element_list):
        title = ' '.join(e[x] for x in word_list)
        payload = '/select_element_by_position{{"position":"{}"}}'.format(i+1)
        buttons.append({'title': title, 'payload': payload})
    return buttons


def get_buttons_relation_list(element_type):
    relation_list = database.get_element_properties(element_type)['relation_list']
    buttons = []
    for r in relation_list:
        title = r['type']
        payload = '/view_element_{}'.format(r['type'])
        buttons.append({'title': title, 'payload': payload})
    return buttons
