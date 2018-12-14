import logging

from modules.patterns import nlu, msg_simple
from modules.actions import executors

logger = logging.getLogger(__name__)

# todo: make it better
INTENT_THRESHOLD = 0.5
ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3


def run_action_from_parsed_message(parsed_message):
    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')

    entities = dict()
    for e in parsed_message.get('entities'):
        entities[e['entity']] = e['value']

    if intent_confidence >= INTENT_THRESHOLD:

        if intent_name == nlu.INTENT_VIEW_RELATED_ELEMENT:
            return executors.action_view_element_related_element(entities)

        elif intent_name == nlu.INTENT_VIEW_RELATIONS:
            return executors.action_view_element_relation_list(entities)

        elif intent_name == nlu.INTENT_SELECT_ELEMENT_BY_POSITION:
            return executors.action_select_element_by_position(entities)

        elif intent_name == nlu.INTENT_FIND_ELEMENT_BY_WORD:
            return executors.action_find_element_by_word(entities)

    messages = []
    msg_simple.ERROR(messages)
    return {'messages': messages}







