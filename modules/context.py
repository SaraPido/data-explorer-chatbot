import logging

"""
The context list is like this one
[
    {
        'type': 'teacher_list', 
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
        ]
    }, 
    {
        'type': 'teacher', 
        'value': {
            'id': 1, 
            'name': 'Nicola', 
            'surname': 'Castaldo', 
            'telephone': '0000000001', 
            'email': 'admin_1@admin.com'
        }
    }
]
"""

logger = logging.getLogger(__name__)
context_list = []


def reset_context_list():
    del context_list[:]


def get_element_from_context_list(element_type):
    """
    Returns None if the element is not found
    :param element_type: the string representing the element
    :return { 'type': 'teacher', 'value': {'id':1, 'name':'t_name' ...} }
    """
    return next(filter(lambda el: el['type'] == element_type, context_list), None)


def get_last_element_from_context_list():
    """
    Returns None if the context_list is empty
    :return: { 'type': 'teacher', 'value': {'id':1, 'name':'t_name' ...} }
    """
    if context_list:
        return context_list[-1]
    else:
        return None


def add_element_to_context_list(element_type, element):
    """
    Add the element independently
    :param element: {'id':1, 'name':'t_name' ...}
    :param element_type: the string representing the element
    """
    context_list.append({'type': element_type, 'value': element})
    logger.info(' ')
    logger.info(' *** Element ' + element_type + ' has been added to the context_list ***')
    print_context_list()


def pop_element_and_leaves_from_context_list(element_type):
    size = len(context_list)
    index = next((i for i, v in enumerate(context_list) if v['type'] == element_type), size)
    del context_list[index:]
    if index != size:
        logger.info(' ')
        logger.info(' *** Element ' + element_type + ' and its leaves has been deleted from the context_list ***')
        logger.info(' ')


''' printer '''


def print_context_list():
    """
    Logs the context_list in a human-readable way
    :return: None
    """
    logger.info(' ')
    sep = ' * '
    for el in context_list:
        if not isinstance(el['value'], list):
            logger.info(sep + el['type'] + ': ' + str(el['value']))
        else:
            logger.info(sep + el['type'] + ':')
            for obj in el['value']:
                logger.info(sep + '- ' + str(obj))
    logger.info(' ')


reset_context_list()
