import logging

"""
The context list is like this one
[
    {
        'name': 'teacher_list', 
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
        'name': 'teacher', 
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


def get_element_from_context_list(element_name):
    """
    Returns None if the element is not found
    :param element_name: the string representing the element
    :return { 'name': 'teacher', 'value': {'id':1, 'name':'t_name' ...} }
    """
    return next(filter(lambda el: el['name'] == element_name, context_list), None)


def get_last_element_from_context_list():
    """
    Returns None if the context_list is empty
    :return: { 'name': 'teacher', 'value': {'id':1, 'name':'t_name' ...} }
    """
    if context_list:
        return context_list[-1]
    else:
        return None


def add_element_to_context_list(element_name, element):
    """
    Add the element independently
    # action..(?)
    :param element: {'id':1, 'name':'t_name' ...}
    :param element_name: the string representing the element
    """
    context_list.append({'name': element_name, 'value': element})
    logger.info(' ')
    logger.info(' *** Element ' + element_name + ' has been added to the context_list ***')
    print_context_list()


def go_back_to_position(position):
    del context_list[position:]


def decorate_last_element_with_action_name(action_name):
    context_list[-1]['action_name'] = action_name


def get_action_name_and_position_list():
    res = []
    for i, e in enumerate(context_list):
        if e.get('action_name'):
            res.append([e['action_name'], i+1])
    return res


def pop_element_and_leaves_from_context_list(element_name):
    size = len(context_list)
    index = next((i for i, v in enumerate(context_list) if v['name'] == element_name), size)
    del context_list[index:]
    if index != size:
        logger.info(' ')
        logger.info(' *** Element ' + element_name + ' and its leaves has been deleted from the context_list ***')
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
        if el.get('action_name'):
            logger.info('>> ' + el['action_name'].upper() + ' >>')
        if not isinstance(el['value'], list):
            logger.info(sep + el['name'] + ': ' + str(el['value']))
        else:
            logger.info(sep + el['name'] + ':')
            for obj in el['value']:
                logger.info(sep + '- ' + str(obj))
    logger.info(' ')


reset_context_list()
