import os

file_path = os.path.normpath(os.path.abspath(__file__))
file_path_list = file_path.split(os.sep)

while file_path_list[-1] != 'sherbot':
    del file_path_list[-1]

DIR_PATH = os.sep.join(file_path_list) + '/'

LOG_PATH_FILE = DIR_PATH + 'log.txt'

DB_PROPERTIES_PATH = DIR_PATH + 'resources/db_properties.json'

NLU_CONFIG_PATH = DIR_PATH + 'resources/nlu/data/nlu_config.yml'
NLU_DATA_PATH = DIR_PATH + 'resources/nlu/data/nlu_data.md'
NLU_MODEL_PATH = DIR_PATH + 'resources/nlu/models/default/nlu_model'

NLU_MODEL_DIR_PATH = DIR_PATH + 'resources/nlu/models'


# testing here

DB_CONCEPT_PATH = DIR_PATH + 'resources/db_concept.json'
DB_SCHEMA_PATH = DIR_PATH + 'resources/db_schema.json'
