import logging
import os
from logging import handlers

from modules.settings import LOG_DIR_PATH_AND_SEP, ELEMENT_VISU_LIMIT, CONTEXT_VISU_LIMIT

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
    'action_name': 'TODO'
}
"""


class Context:

    def __init__(self, chat_id):
        self.context_list = []
        self.reset_show_context_list = True
        self.context_list_indices = {'from': 0, 'to': 0}
        self.reset_show_last_element = True
        self.logger = logging.Logger(__name__, logging.INFO)
        # self.log_path = LOG_DIR_PATH_AND_SEP + str(chat_id) + '.txt'
        # log_handler = handlers.RotatingFileHandler(self.log_path, maxBytes=500)
        # log_handler.setLevel(logging.INFO)
        # self.logger.addHandler(log_handler)

    def reset_context_list(self):
        del self.context_list[:]

    def get_element_by_name(self, element_name):
        """
        Returns None if the element is not found
        """
        return next(filter(lambda el: el['element_name'] == element_name, self.context_list), None)

    def get_last_element(self):
        """
        Returns None if the context_list is empty
        """
        return self.context_list[-1] if self.context_list else None

    def view_last_element(self):
        if self.reset_show_last_element:
            self.show_last_element_from_start()
        self.reset_show_last_element = True
        return self.get_last_element()

    def append_element(self, element):
        # NEW feature: deletes the element of the same type and all its predecessor
        # the search is limited to the context excluding the last element
        """ NEW FEATURE HERE
        index = -1
        for i, el in enumerate(self.context_list):
            if el['element_name'] == element['element_name'] and i < len(self.context_list) - 1:  # keep the last
                index = i
                break
        if index > -1:
            self.logger.info('Removing elements from the context list, total: {}'.format(index + 1))
            for i in range(index + 1):
                self.context_list.pop(0)
        """

        self.context_list.append(element)
        self.show_last_element_from_start()
        self.logger.info(' ')
        self.logger.info(' *** Element ' + element['element_name'] + ' has been added to the context_list ***')
        self.update_log()

    def show_last_element_from_start(self):
        element = self.context_list[-1]
        if element['real_value_length'] > 1:
            element['show'] = {'from': 0, 'to': min(ELEMENT_VISU_LIMIT, element['real_value_length'])}

    def go_back_to_position(self, position):
        del self.context_list[position:]
        self.show_last_element_from_start()

    def get_context_list(self):
        return self.context_list

    def view_context_list(self):
        if self.reset_show_context_list:
            self.show_context_list_from_start()
        self.reset_show_context_list = True
        return self.get_context_list()

    def show_context_list_from_start(self):
        self.context_list_indices['from'] = max(len(self.context_list) - CONTEXT_VISU_LIMIT, 0)
        self.context_list_indices['to'] = len(self.context_list)

    def update_log(self):
        """
        Logs the context_list in a human-readable way
        """
        self.logger.info(' ')
        sep = ' * '
        for el in self.context_list:

            self.logger.info(sep + 'name: ' + el.get('element_name'))
            query = el.get('query')
            if query:
                self.logger.info(sep + 'q_string: ' + query.get('q_string'))
                self.logger.info(sep + 'q_tuple: ' + str(query.get('q_tuple')))
            self.logger.info(sep + 'action_name: ' + el.get('action_name'))
            self.logger.info(sep + 'real_value_length: ' + str(el.get('real_value_length')))
            for i, obj in enumerate(el['value']):
                self.logger.info(sep + '- ' + str(obj))
            if el.get('show'):
                self.logger.info(sep + 'showing from {} to {}'.format(el['show']['from'], el['show']['to']))
            self.logger.info(' ')

