import logging

from modules.actions import executors

logger = logging.getLogger(__name__)

# todo: make it better
INTENT_THRESHOLD = 0.4


def run_action_from_parsed_message(parsed_message):
    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')

    """
    entities = dict()
    for e in parsed_message.get('entities'):
        entities[e['entity']] = e['value']
    """
    entities = parsed_message.get('entities')

    if intent_confidence >= INTENT_THRESHOLD:
        return executors.execute_action_from_intent_name(intent_name, entities)
    else:
        return executors.execute_fallback()






