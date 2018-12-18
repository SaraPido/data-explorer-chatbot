from modules.database import resolver


def ELEMENT_ATTRIBUTES(messages, element_type, element_value):
    msg = '{}\n'.format(element_type.upper())
    msg += '\n'.join(['- {0}: {1}'.format(k, v) for k, v in element_value.items()])
    messages.append(msg)


def LIST_OF_ELEMENTS(messages, element_type, element_value_list):
    show_column_list = resolver.get_element_properties(element_type)['show_column_list']
    message = 'i. ' + ', '.join(x.upper() for x in show_column_list) + '\n\n'
    for i, e in enumerate(element_value_list):
        message += '{}. '.format(i + 1)

        if show_column_list:
            message += ', '.join('{}'.format(e[x]) for x in show_column_list)

        if i != len(element_value_list) - 1:
            message += '\n'

    messages.append(message)


