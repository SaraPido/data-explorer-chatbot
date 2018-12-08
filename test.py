import logging
import warnings

from threading import Thread
from time import sleep

from modules import database, connectors, extractor, caller
from modules.settings import LOG_PATH_FILE, DB_PROPERTIES_PATH


def console_input():

    print('Write a sentence or write "exit"')
    while True:
        message = input()
        if 'exit' == message.lower():
            break

        parsed_message = extractor.parse(message)
        result = caller.run_action_from_parsed_message(parsed_message)

        print(result.get('message'))
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

    database.connect()
    database.load_db_properties(DB_PROPERTIES_PATH)

    extractor.load_model()

    logging.info('Bot successfully started!')

    connectors.start()

    # console.input()
    while 1:
        sleep(100)

