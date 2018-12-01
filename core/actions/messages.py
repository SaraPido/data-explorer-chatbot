from server.core import database


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
