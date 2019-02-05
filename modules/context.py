import logging

"""
{
    'query': {
        'q_string': 'SELECT DISTINCT a.customerNumber, a.customerName, a.contactLastName, a.contactFirstName, '
                    'a.phone, a.addressLine1, a.addressLine2, a.city, a.state, a.postalCode, a.country, '
                    'a.salesRepEmployeeNumber, a.creditLimit '
                    'FROM customers a '
                    'WHERE ( a.city = %s OR a.state = %s OR a.country = %s )',
        'q_tuple': ('london', 'london', 'london')
    },
    'value': [
        {
            'customerNumber': 324,
            'customerName': 'Stylish Desk Decors, Co.',
            'contactLastName': 'Brown',
            'contactFirstName': 'Ann ',
            'phone': '(171) 555-0297',
            'addressLine1': '35 King George',
            'addressLine2': None,
            'city': 'London',
            'state': None,
            'postalCode': 'WX3 6FW',
            'country': 'UK',
            'salesRepEmployeeNumber': 1501,
            'creditLimit': "Decimal('77000.00')"
        },
        {
            'customerNumber': 489,
            'customerName': 'Double Decker Gift Stores, Ltd',
            'contactLastName': 'Smith',
            'contactFirstName': 'Thomas ',
            'phone': '(171) 555-7555',
            'addressLine1': '120 Hanover Sq.',
            'addressLine2': None,
            'city': 'London',
            'state': None,
            'postalCode': 'WA1 1DP',
            'country': 'UK',
            'salesRepEmployeeNumber': 1501,
            'creditLimit': "Decimal('43300.00')"
         }
    ], 
    'by_value': [],
    'show': {
        "from": 1,
        "to": 5
    }   
    'real_value_length': 2,
    'element_name': 'customer', 
    'action_description': 'TODO'
}
"""

logger = logging.getLogger(__name__)
context_list = []


def reset_context_list():
    del context_list[:]


def get_element_by_name(element_name):
    """
    Returns None if the element is not found
    """
    return next(filter(lambda el: el['element_name'] == element_name, context_list), None)


def get_last_element():
    """
    Returns None if the context_list is empty
    """
    return context_list[-1] if context_list else None


def append_element(element):
    # NEW feature: deletes the element of the same type and all its predecessor
    # the search is limited to the context excluding the last element
    index = -1
    for i, el in enumerate(context_list):
        if el['element_name'] == element['element_name'] and i < len(context_list) - 1:  # keep the last
            index = i
            break
    if index > -1:
        logger.info('Removing elements from the context list, total: {}'.format(index + 1))
        for i in range(index + 1):
            context_list.pop(0)

    context_list.append(element)
    logger.info(' ')
    logger.info(' *** Element ' + element['element_name'] + ' has been added to the context_list ***')
    update_log()


def go_back_to_position(position):
    del context_list[position:]
    # todo check correctness
    if context_list[position-1].get('show'):
        del context_list[position-1]['show']


def get_action_name_list():
    return [e['action_description'] for e in context_list]


def update_log():
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
        if el.get('show'):
            logger.info(sep + 'showing from {} to {}'.format(el['show']['from'], el['show']['to']))
        logger.info(' ')


reset_context_list()
