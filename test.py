import logging
import warnings

from time import sleep

from modules import connectors, extractor, caller
from modules.database import resolver, broker
from modules.settings import LOG_PATH


def console_input():

    print('Write a sentence or write "exit"')
    while True:
        message = input()
        if 'exit' == message.lower():
            break

        parsed_message = extractor.parse(message)
        response = caller.run_action_from_parsed_message(parsed_message)

        print(response.get_printable_string())


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    with open(LOG_PATH, 'w'):
        pass
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO)

    logging.info('Starting the bot...')

    resolver.load_db_concept()
    broker.load_db_schema()
    broker.connect()
    extractor.load_model()

    logging.info('Bot successfully started!')

    connectors.start()
    #console_input()
    while 1:
        sleep(100)

