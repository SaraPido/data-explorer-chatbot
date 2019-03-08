import os

file_path = os.path.normpath(os.path.abspath(__file__))
file_path_list = file_path.split(os.sep)
file_sep = os.sep


# selector

select = 'classicmodels'

select_dict = {
    'employees': ['a', 'employees'],
    'school': ['b', 'rasa_db'],
    'classicmodels': ['c', 'classicmodels']
}

abc = select_dict[select][0]
db_name = select_dict[select][1]


# files

while file_path_list[-1] != 'sherbot':
    del file_path_list[-1]

DIR_PATH = os.sep.join(file_path_list)

LOG_DIR_PATH_AND_SEP = file_sep.join([DIR_PATH, 'logs']) + file_sep
NLU_DATA_PATH = file_sep.join([DIR_PATH, 'writer']) + file_sep + 'rasa_dataset_training.json'
NLU_MODEL_PATH = file_sep.join([DIR_PATH, 'resources', 'nlu', 'models', 'default', 'nlu_model'])
NLU_MODEL_DIR_PATH = file_sep.join([DIR_PATH, 'resources', 'nlu', 'models'])
DB_CONCEPT_PATH = file_sep.join([DIR_PATH, 'resources', 'db']) + file_sep + 'db_concept_' + abc + '.json'
DB_SCHEMA_PATH = file_sep.join([DIR_PATH, 'resources', 'db']) + file_sep + 'db_schema_' + abc + '.json'

CHATITO_TEMPLATE_PATH = file_sep.join([DIR_PATH, 'writer', 'chatito_template.chatito'])
CHATITO_MODEL_PATH = file_sep.join([DIR_PATH, 'writer', 'chatito_model.chatito'])

# settings

INTENT_CONFIDENCE_THRESHOLD = 0.4
ELEMENT_SIMILARITY_DISTANCE_THRESHOLD = 3
ELEMENT_VISU_LIMIT = 5
CONTEXT_VISU_LIMIT = 4

CONTEXT_PERSISTENCE_SECONDS = 5 * 60
CONTEXT_MAX_LENGTH = 8

QUERY_LIMIT = 100  # 0 for no limit

#db

remote = True if os.environ.get('PYTHONANYWHERE_SITE') else False

DATABASE_USER = 'nicolacastaldo' if remote else 'root'
DATABASE_PASSWORD = 'dataexplorerbot' if remote else 'admin'
DATABASE_HOST = 'nicolacastaldo.mysql.pythonanywhere-services.com' if remote else '127.0.0.1'
DATABASE_NAME = 'nicolacastaldo$classicmodels' if remote else db_name

# nlu

NLU_CONFIG_PIPELINE = "tensorflow_embedding"  # "spacy_sklearn"
NLU_CONFIG_LANGUAGE = "en"
