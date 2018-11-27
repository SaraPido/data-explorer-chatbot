import logging

from gevent.pywsgi import WSGIServer
from rasa_core_sdk import endpoint as edp

from server.core import database
from server.core.actions import handlers

SERVER_PORT = 5055
ACTIONS_MODULE_PATH = 'core.actions.register'
DB_PROPERTIES_PATH = 'resources/db_properties.json'


def start_server():
    logging.info('Starting action endpoint server...')
    edp_app = edp.endpoint_app(cors_origins=None, action_package_name=ACTIONS_MODULE_PATH)
    http_server = WSGIServer(('0.0.0.0', SERVER_PORT), edp_app)
    http_server.start()

    logging.info('Action endpoint is up and running on {}'.format(http_server.address))
    http_server.serve_forever()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    database.connect()
    handlers.load_db_properties(DB_PROPERTIES_PATH)

    start_server()
