from modules.database import resolver


def get_message_word_column_list_with_attribute(element_type, element_list, attribute_type):
    word_column_list = resolver.get_element_properties(element_type)['word_column_list']
    message = ''
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in word_column_list)
        message += ': ' + str(e[attribute_type])
        if i != len(element_list) - 1:
            message += '\n'
    return message


def get_message_word_column_list(element_type, element_list):
    word_column_list = resolver.get_element_properties(element_type)['word_column_list']
    message = ''
    for i, e in enumerate(element_list):
        message += '- '
        message += ' '.join(e[x] for x in word_column_list)
        if i != len(element_list) - 1:
            message += '\n'
    return message
