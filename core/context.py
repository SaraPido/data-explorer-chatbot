import logging

logger = logging.getLogger(__name__)


''' find element '''


def reset_context_list():
    global context_list
    context_list = []


def get_element_from_context_list(element_type):
    element = next(filter(lambda el: el['type'] == element_type, context_list), None)
    if element:
        return element['value']
    else:
        return None


def get_last_element_from_context_list():
    ''' It also returns the type '''
    if context_list:
        return context_list[-1]
    else:
        return None


def add_element_to_context_list(element_type, element):
    context_list.append({'type': element_type, 'value': element})
    logger.info(' ')
    logger.info(' *** Element ' + element_type + ' has been added to the context_list ***')
    print_context_list(context_list)


def pop_element_and_leaves_from_context_list(element_type):
    size = len(context_list)
    index = next((i for i, v in enumerate(context_list) if v['type'] == element_type), size)
    del context_list[index:]
    if index != size:
        logger.info(' ')
        logger.info(' *** Element ' + element_type + ' and its leaves has been deleted from the context_list ***')
        logger.info(' ')


''' printer '''


def print_context_list(lis):
    logger.info(' ')
    sep = ' * '
    for el in lis:
        if not isinstance(el['value'], list):
            logger.info(sep + el['type'] + ': ' + str(el['value']))
        else:
            logger.info(sep + el['type'] + ':')
            for obj in el['value']:
                logger.info(sep + '- ' + str(obj))
    logger.info(' ')


reset_context_list()