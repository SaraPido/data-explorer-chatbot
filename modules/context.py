import logging

from modules import common

"""
[
    {
        'name': 'teacher',
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
    """
    return next(filter(lambda el: el['name'] == element_name, context_list), None)


def get_last_element_from_context_list():
    """
    Returns None if the context_list is empty
    """
    return context_list[-1] if context_list else None


def add_element_to_context_list(name,
                                query,
                                action_description,
                                value,
                                real_value_length=None):
    # adjust real_value_length
    real_value_length = real_value_length if real_value_length else len(value)

    # create dictionary with keys as variable names
    d = common.get_dict(name, query, action_description, value, real_value_length)
    context_list.append(d)

    logger.info(' ')
    logger.info(' *** Element ' + name + ' has been added to the context_list ***')
    print_context_list()


def go_back_to_position(position):
    del context_list[position:]


def get_action_name_and_position_list():
    res = []
    for i, e in enumerate(context_list):
        res.append([e['action_description'], i + 1])
    return res


"""
def pop_element_and_leaves_from_context_list(element_name):
    size = len(context_list)
    index = next((i for i, v in enumerate(context_list) if v['name'] == element_name), size)
    del context_list[index:]
    if index != size:
        logger.info(' ')
        logger.info(' *** Element ' + element_name + ' and its leaves has been deleted from the context_list ***')
        logger.info(' ')
"""

''' printer '''


def print_context_list():
    """
    Logs the context_list in a human-readable way
    """
    logger.info(' ')
    sep = ' * '
    for el in context_list:

        logger.info(sep + 'name: ' + el.get(['name']))
        logger.info(sep + 'query: ' + el.get(['query']))
        logger.info(sep + 'action_description: ' + el.get(['action_description']))
        logger.info(sep + 'real_value_length: ' + el.get(['real_value_length']))
        for obj in el['value']:
            logger.info(sep + '- ' + str(obj))
        logger.info(' ')


reset_context_list()

