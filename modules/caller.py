import logging

from modules import conversation
from modules.actions import executors

logger = logging.getLogger(__name__)

# todo: make it better
INTENT_THRESHOLD = 0.4

context_dict = {}


def run_action_from_parsed_message(parsed_message, chat_id):

    intent_confidence = parsed_message.get('intent').get('confidence')
    intent_name = parsed_message.get('intent').get('name')

    entities = parsed_message.get('entities')

    if intent_confidence >= INTENT_THRESHOLD:
        context = get_context(chat_id)
        return executors.execute_action_from_intent_name(intent_name, entities, context)
    else:
        return executors.execute_fallback()


def get_context(chat_id):

    # conversation was already defined
    if context_dict.get(chat_id):

        # todo some log

        # schedule_delete_event(chat_id)
        return context_dict[chat_id]

    else:

        # todo some log

        context = conversation.Context(chat_id)
        context_dict[chat_id] = context
        # schedule_delete_event(chat_id)
        return context


def schedule_delete_event(chat_id):
    pass
