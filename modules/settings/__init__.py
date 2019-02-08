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
NLU_DATA_PATH = file_sep.join([DIR_PATH, 'resources', 'nlu', 'data']) + file_sep + 'nlu_data_' + abc + '.md'
NLU_MODEL_PATH = file_sep.join([DIR_PATH, 'resources', 'nlu', 'models', 'default', 'nlu_model'])
NLU_MODEL_DIR_PATH = file_sep.join([DIR_PATH, 'resources', 'nlu', 'models'])
DB_CONCEPT_PATH = file_sep.join([DIR_PATH, 'resources', 'db']) + file_sep + 'db_concept_' + abc + '.json'
DB_SCHEMA_PATH = file_sep.join([DIR_PATH, 'resources', 'db']) + file_sep + 'db_schema_' + abc + '.json'

# settings

#db

DATABASE_USER = 'root'
DATABASE_PASSWORD = 'admin'
DATABASE_HOST = '127.0.0.1'
DATABASE_NAME = db_name

# nlu

NLU_CONFIG_PIPELINE = "tensorflow_embedding"  # "spacy_sklearn"
NLU_CONFIG_LANGUAGE = "en"
