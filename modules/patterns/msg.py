from modules.database import resolver

HI_THERE = 'Hi there explorator!\n' \
           'Here is a few examples of what you can ask me:'
ERROR = 'Sorry, I did not get that! :('
FINDING_ELEMENT = 'Let me check...'
NOTHING_FOUND = 'Nothing has been found, I am sorry!'
ONE_RESULT_FOUND = 'Et voilà! I found 1 result!'
N_RESULTS_FOUND_PATTERN = 'Et voilà! I found {} results!'
SELECT_FOR_INFO = 'Select the one you are interested in:'
INTRODUCE_ELEMENT_TO_SHOW_PATTERN = 'Here is what I know about this {}:'
EMPTY_CONTEXT_LIST = 'I am sorry, but your conversation history is empty!'
CONTEXT_LIST_RESET = 'The history has been reset!'
SHOW_CONTEXT_INFO = 'Click a button to go back in the history!'


def element_attributes(element):
    msg = '{}\n'.format(element['element_name'].upper())
    # taking only first value
    msg += '\n'.join(['- {0}: {1}'.format(k, v) for k, v in element['value'][0].items()])
    return msg


def find_element_action_name(element_name, ordered_entities):
    stringified_entities = []
    for oe in ordered_entities:
        se = '"'
        if oe.get('attribute'):
            se += oe['attribute'] + ' '
        se += str(oe['value']) + '"'
        stringified_entities.append(se)
    return '[Finding by attributes] {}'.format(element_name, ' ,'.join(stringified_entities))

# ------

# ------


def LIST_OF_ELEMENTS_FUNCTION(element):
    """
    DEPRECATED
    """
    show_column_list = resolver.extract_show_columns(element['element_name'])
    message = 'i. ' + ', '.join(x.upper() for x in show_column_list) + '\n'
    for i, e in enumerate(element['value']):
        message += '{}. '.format(i + 1)

        if show_column_list:
            message += ', '.join('{}'.format(e[x]) for x in show_column_list)

        if i != len(element['value']) - 1:
            message += '\n'
    return message
