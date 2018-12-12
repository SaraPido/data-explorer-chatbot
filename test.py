import logging
import warnings

from time import sleep

from modules import connectors, extractor, caller
from modules.database import resolver, broker
from modules.settings import LOG_PATH_FILE, DB_CONCEPT_PATH, DB_SCHEMA_PATH


def console_input():

    print('Write a sentence or write "exit"')
    while True:
        message = input()
        if 'exit' == message.lower():
            break

        parsed_message = extractor.parse(message)
        result = caller.run_action_from_parsed_message(parsed_message)

        print(result.get('messages'))
        buttons = result.get('buttons')
        if buttons:
            for b in buttons:
                print('{} => {}'.format(b['title'], b['payload']))


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    with open(LOG_PATH_FILE, 'w'):
        pass
    logging.basicConfig(filename=LOG_PATH_FILE, level=logging.INFO)

    logging.info('Starting the bot...')

    resolver.load_db_concept(DB_CONCEPT_PATH)
    broker.load_db_schema(DB_SCHEMA_PATH)
    broker.connect()
    extractor.load_model()

    logging.info('Bot successfully started!')

    connectors.start()
    #console_input()
    while 1:
        sleep(100)

