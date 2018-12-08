import logging

from modules.actions import executors

logger = logging.getLogger(__name__)

# todo: make it better
THRESHOLD = 0.5


def run_action_from_parsed_message(parsed_message):
    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')
    entities = parsed_message.get('entities')

    if intent_confidence >= THRESHOLD:

        element_type = next(iter([e.get('value') for e in entities if e.get('entity') == 'element']), None)

        word = next(iter([e.get('value') for e in entities if e.get('entity') == 'word']), None)

        position = next(iter([e.get('value') for e in entities if e.get('entity') == 'position']), '0')

        int_pos = int(position)

        if intent_name == 'view_related_element':
            if element_type:
                return executors.action_view_element_related_element(element_type, int_pos)

        elif intent_name == 'view_relations':
            return executors.action_view_element_relation_list()

        elif intent_name == 'select_element_by_position':
            return executors.action_select_element_by_position(int_pos)

        elif intent_name == 'find_element_by_word':
            if word and element_type:
                return executors.action_find_element_by_word(element_type, word)

    return {'messages': ['I did not understand that :(']}
