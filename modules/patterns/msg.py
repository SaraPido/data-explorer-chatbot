import random

from modules.database import resolver

HI_THERE = 'Hi there! Let me introduce myself...\n'\
           'I am a chatbot for Data Exploration and I will help you during the navigation of a relational database.'
REMEMBER_HISTORY = "You can always check the history of the conversation, just ask!\n " \
                   "For instance you can try with: \"show me the history\" or maybe just \"history\".\n" \
                   "I will help you to go back in the past, if you want, or just reset it completely."
REMEMBER_GO_BACK = "If you did something wrong, DON'T PANIC!\n" \
                   "By simply telling me something like \"go back\" or \"undo\" you can jump to the " \
                   "previous element of your history.\n" \
                   "This might be a shortcut when you want to make little rollbacks, " \
                   "without accessing all your history."
ERROR = 'Sorry, I did not get that! :('
FINDING_ELEMENT = 'Let me check...'
NOTHING_FOUND = 'Nothing has been found, I am sorry!'
ONE_RESULT_FOUND = 'Et voilà! I found 1 result!'
N_RESULTS_FOUND_PATTERN = 'Et voilà! I found {} results!'
REMEMBER_FILTER = 'Remember that you can always filter them, click the following button to get some hints...'
SELECT_FOR_INFO_PATTERN = 'Select the element of type {} you are interested in.'
INTRODUCE_ELEMENT_TO_SHOW_PATTERN = 'Here is what I know about this {}:'
EMPTY_CONTEXT_LIST = 'I am sorry, but your conversation history is empty!'
CONTEXT_LIST_RESET = 'The history has been reset!'
REMEMBER_RESET_HISTORY = 'If you want you can reset the history of the conversation ' \
                         'by clicking at the following button:'


def element_attributes(element):
    msg = '{}\n'.format(element['element_name'].upper())
    # taking only first value
    msg += '\n'.join(['- {0}: {1}'.format(k, v) for k, v in element['value'][0].items()])
    return msg


def element_list(element):
    msg = ''
    for i in range(element['show']['from'], element['show']['to']):
        msg += '{}. {}\n'.format(i+1, resolver.get_element_show_string(element['element_name'], element['value'][i]))
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


def element_names_examples():
    elements = resolver.get_all_primary_element_names()
    message = 'Currently I understand phrases related to some elements, which are: '
    message += ', '.join(elements) + '.'
    return message


def element_names_info_examples():
    elements = resolver.get_all_primary_element_names()
    message = 'You can ask me more information about a specific element. For example you can try with:\n'
    message += '- tell me more about {}'.format(elements[0])
    return message


def find_element_examples(element_name):
    message = 'I am able to find elements of type {} in many different ways. ' \
              'Here some options, I hope they can fit your purposes!\n'.format(element_name)

    attributes = resolver.extract_all_attributes(element_name)
    all_el_names = [element_name] + resolver.get_element_aliases(element_name)
    if attributes:  # will be deleted when all elements will have at least 1 attribute
        for a in attributes:
            message += "- Find {} ".format(random.choice(all_el_names))
            if a.get('keyword'):
                message += "{} ".format(a['keyword'])
            if a.get('type') == 'num':
                message += "more than / less than "
            message += "...\n"

    else:
        message = '- no attribute has been defined for {} yet -'.format(element_name)

    return message


def filter_element_examples(element_name):
    message = 'How to filter elements of type {}? Here some hints:\n'.format(element_name)
    attributes = resolver.extract_all_attributes(element_name)
    if attributes:  # will be deleted when all elements will have at least 1 attribute
        for a in attributes:
            message += "- Filter those "
            if a.get('keyword'):
                message += "{} ".format(a['keyword'])
            if a.get('type') == 'num':
                message += "more than " if random.randint(0, 1) else "less than "
            message += "...\n"
    else:
        message = '- no attribute has been defined for {} yet -'.format(element_name)

    return message

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
