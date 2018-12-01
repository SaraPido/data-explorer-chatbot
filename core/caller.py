import logging

from server.core.actions import executors

logger = logging.getLogger(__name__)

# todo: make it better
THRESHOLD = 0.6


def run_action_from_parsed_message(parsed_message):

    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')
    entities = parsed_message.get('entities')

    if intent_confidence >= THRESHOLD:

        if intent_name.startswith('view_element_'):

            attribute = intent_name[len('view_element_'):]

            if attribute == 'column_list':
                return executors.action_view_element_column_list()

            else:
                return executors.action_view_element_attribute(attribute)

        intent_name_list = intent_name.split('_')

        if intent_name_list[0] == 'find':
            # e.g
            # 0..._1......_2._3...
            # find_teacher_by_word

            element_type = intent_name_list[1]

            if intent_name_list[3] == 'word':
                word = next(iter([e.get('value') for e in entities if e.get('entity') == 'word']), None)

                if word:
                    return executors.action_find_element_by_word(element_type, word)

    return {'message': 'I did not understand that :('}
