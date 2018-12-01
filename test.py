import logging
import os

from server.core import database, caller, extractor

LOG_PATH_FILE = 'log.txt'

# SERVER_PORT = 5055
# ACTIONS_MODULE_PATH = 'core.actions.register'
DB_PROPERTIES_PATH = 'resources/db_properties.json'

DEBUG = False


def start_server():

    extractor.load_model()

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


    '''
    logging.info('Starting action endpoint server...')
    edp_app = edp.endpoint_app(cors_origins=None, action_package_name=ACTIONS_MODULE_PATH)
    http_server = WSGIServer(('0.0.0.0', SERVER_PORT), edp_app)
    http_server.start()

    logging.info('Action endpoint is up and running on {}'.format(http_server.address))
    http_server.serve_forever()
    '''


if __name__ == '__main__':

    with open(LOG_PATH_FILE, 'w'):
        pass
    logging.basicConfig(filename=LOG_PATH_FILE, level=logging.INFO)

    database.connect()
    database.load_db_properties(os.path.abspath(DB_PROPERTIES_PATH))

    start_server()
