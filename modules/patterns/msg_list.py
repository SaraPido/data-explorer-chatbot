from modules.database import resolver


def ELEMENT_ATTRIBUTES(messages, element):
    msg = '{}\n'.format(element['element_name'].upper())
    # taking only first value
    msg += '\n'.join(['- {0}: {1}'.format(k, v) for k, v in element['value'][0].items()])
    messages.append(msg)


def LIST_OF_ELEMENTS(messages, element):
    show_column_list = resolver.get_element(element['element_name'])['show_columns']
    message = 'i. ' + ', '.join(x.upper() for x in show_column_list) + '\n'
    for i, e in enumerate(element['value']):
        message += '{}. '.format(i + 1)

        if show_column_list:
            message += ', '.join('{}'.format(e[x]) for x in show_column_list)

        if i != len(element['value']) - 1:
            message += '\n'

    messages.append(message)


