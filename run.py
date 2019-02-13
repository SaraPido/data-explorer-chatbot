import logging
import warnings

from time import sleep

from modules import extractor, caller
from modules.connectors import telegram
from modules.database import resolver, broker
from modules.settings import LOG_DIR_PATH_AND_SEP


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

    log_path = LOG_DIR_PATH_AND_SEP + 'sherbot.log'
    with open(log_path, 'w'):
        pass
    logging.basicConfig(filename=log_path, level=logging.INFO)

    logging.info('Starting the bot...')

    resolver.load_db_concept()
    broker.load_db_schema()
    broker.connect()
    extractor.load_model()

    logging.info('Bot successfully started!')

    telegram.start()
    # console_input()
    while 1:
        sleep(100)

