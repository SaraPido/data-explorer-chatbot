import logging

from modules.actions import executors
from modules import patterns

logger = logging.getLogger(__name__)

# todo: make it better
THRESHOLD = 0.5


def run_action_from_parsed_message(parsed_message):
    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')
    entities = parsed_message.get('entities')

    if intent_confidence >= THRESHOLD:

        element_type = extract_entity_if_present(entities, patterns.ENTITY_ELEMENT_TYPE)
        by_element_type = extract_entity_if_present(entities, patterns.ENTITY_BY_ELEMENT_TYPE)
        word = extract_entity_if_present(entities, patterns.ENTITY_WORD)
        position = int(extract_entity_if_present(entities, patterns.ENTITY_POSITION, otherwise=0))

        if intent_name == patterns.INTENT_VIEW_RELATED_ELEMENT:
            if element_type:
                return executors.action_view_element_related_element(element_type, by=by_element_type, position=position)

        elif intent_name == patterns.INTENT_VIEW_RELATIONS:
            return executors.action_view_element_relation_list()

        elif intent_name == patterns.INTENT_SELECT_ELEMENT_BY_POSITION:
            return executors.action_select_element_by_position(position)

        elif intent_name == patterns.INTENT_FIND_ELEMENT_BY_WORD:
            if word and element_type:
                return executors.action_find_element_by_word(element_type, word)

    return {'messages': ['I did not understand that :(']}


def extract_entity_if_present(entities, entity_name, otherwise=None):
    return next(
        iter(
            [e.get('value')
             for e in entities
             if e.get('entity') == entity_name]
        ),
        otherwise
    )
