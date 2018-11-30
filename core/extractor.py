import logging

from rasa_nlu.model import Interpreter

logger = logging.getLogger(__name__)

inter = None


def load_model(model_path):
    global inter
    logger.info('Loading the NLU model WITHOUT training...')
    inter = Interpreter.load(model_path)
    logger.info('NLU model loaded!')


def parse(message):
    """
    Gives result in the form:
    {
        'intent': {'name': 'find_teacher_by_word', 'confidence': 0.9642855525016785},
        'entities': [
            {'value': 'Nicola', 'entity': 'word'}
        ]
    }
    :param message: the message to be converted
    :return: the dictionary representing the interpretation
    """
    parsed_message = inter.parse(message)
    del parsed_message['intent_ranking'], parsed_message['text']
    for e in parsed_message.get('entities'):
        del e['start'], e['end'], e['confidence'], e['extractor']

    return parsed_message

