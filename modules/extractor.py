import json
import logging

from rasa_nlu import model as nlu_model
from rasa_nlu import training_data as nlu_train

from modules.settings import NLU_DATA_PATH, NLU_MODEL_DIR_PATH, NLU_MODEL_PATH, NLU_CONFIG_PIPELINE, \
    NLU_CONFIG_LANGUAGE

logger = logging.getLogger(__name__)

inter = None


def load_model():
    global inter
    logger.info('NLU model:\n'
                '"' + NLU_MODEL_PATH + '"')
    logger.info('Loading the NLU model WITHOUT training...')
    inter = nlu_model.Interpreter.load(NLU_MODEL_PATH)
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

    logger.info('Message to parse: "{}"'.format(message))

    if message.startswith('/'):
        parsed_message = dict()
        message = message[1:]
        split_message = message.split('{', 1)
        intent_name = split_message[0]
        entities = []
        if len(split_message) > 1:  # if there are entities
            entity_list = split_message[1].split(',')
            for i, e in enumerate(entity_list):
                import re
                matches = re.findall(r'.*(?:\"|\')(.+?)(?:\"|\'):.*(?:\"|\')(.+?)(?:\"|\').*', e)
                entities.append({'entity': matches[0][0], 'value': matches[0][1], 'start': i+1})

        parsed_message['intent'] = {'name': intent_name, 'confidence': 1}
        parsed_message['entities'] = entities
    else:
        parsed_message = inter.parse(message)
        del parsed_message['intent_ranking'], parsed_message['text']
        for e in parsed_message.get('entities'):
            # del e['start']
            del e['end'], e['confidence'], e['extractor']
            if e.get('processors'):
                del e['processors']

    logger.info('Parsed message: {}'.format(parsed_message))
    return parsed_message


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logging.info('NLU model:\n'
                 '"' + NLU_MODEL_PATH + '"')
    logging.info('Training the NLU model...')
    training_data = nlu_train.load_data(NLU_DATA_PATH)
    trainer = nlu_model.Trainer(nlu_model.config.RasaNLUModelConfig({"pipeline": NLU_CONFIG_PIPELINE,
                                                                     "language": NLU_CONFIG_LANGUAGE}))
    trainer.train(training_data)
    model_directory = trainer.persist(NLU_MODEL_DIR_PATH, fixed_model_name='nlu_model')
    logging.info('NLU model completely trained!')


"""
complex pipeline:

pipeline = [{"name": "nlp_spacy"},
            {"name": "tokenizer_spacy"},
            {"name": "intent_entity_featurizer_regex"},
            {"name": "intent_featurizer_spacy"},
            {"name": "ner_crf"},
            {"name": "ner_synonyms"},
            {"name": "intent_classifier_sklearn"}]
            
pipeline = [{"name": "tokenizer_whitespace"},
            {"name": "ner_crf"},
            {"name": "ner_synonyms"},
            {"name": "intent_featurizer_count_vectors"},
            {"name": "intent_classifier_tensorflow_embedding"}]
            
"""
