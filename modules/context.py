import logging

"""
[
    {
        'element_name': 'teacher',
        'query': {
            q_string: 'SELECT * FROM Teacher WHERE name=%s'
            q_tuple: [ 'Nicola' ]
        },
        'action_description': 'Find element teacher with word Nicola',
        'value': [
            {
                'id': 1, 
                'name': 'Nicola', 
                'surname': 'Castaldo', 
                'telephone': '0000000001', 
                'email': 'admin_1@admin.com'
            },
            {
                'id': 6, 
                'name': 'Nicola', 
                'surname': 'Abbagnano', 
                'telephone': '0000000006', 
                'email': 'admin_6@admin.com'
            }
        ],
        'by_value': [
        
        
        ]
        'real_value_length': 2
    }
]

"""

logger = logging.getLogger(__name__)
context_list = []


def reset_context_list():
    del context_list[:]


def get_element_from_context_list(element_name):
    """
    Returns None if the element is not found
    """
    return next(filter(lambda el: el['element_name'] == element_name, context_list), None)


def get_last_element_from_context_list():
    """
    Returns None if the context_list is empty
    """
    return context_list[-1] if context_list else None


def add_element_to_context_list(element):

    # NEW feature: deletes the element of the same type and all its predecessor
    # the search is limited to the context excluding the last element
    index = -1
    for i, el in enumerate(context_list):
        if el['element_name'] == element['element_name'] and i < len(context_list)-1:  # keep the last
            index = i
            break
    if index > -1:
        logger.info('Removing elements from the context list, total: {}'.format(index+1))
        for i in range(index+1):
            context_list.pop(0)

    context_list.append(element)
    logger.info(' ')
    logger.info(' *** Element ' + element['element_name'] + ' has been added to the context_list ***')
    print_context_list()


def go_back_to_position(position):
    del context_list[position:]


def get_action_name_list():
    return [e['action_description'] for e in context_list]


def print_context_list():
    """
    Logs the context_list in a human-readable way
    """
    logger.info(' ')
    sep = ' * '
    for el in context_list:

        logger.info(sep + 'name: ' + el.get('element_name'))
        query = el.get('query')
        if query:
            logger.info(sep + 'q_string: ' + query.get('q_string'))
            logger.info(sep + 'q_tuple: ' + str(query.get('q_tuple')))
        logger.info(sep + 'action_description: ' + el.get('action_description'))
        logger.info(sep + 'real_value_length: ' + str(el.get('real_value_length')))
        for i, obj in enumerate(el['value']):
            logger.info(sep + '- ' + str(obj))
            if el.get('by_value'):
                logger.info(sep + 'BY: - ' + str(el['by_value'][i]))
        logger.info(' ')


reset_context_list()

