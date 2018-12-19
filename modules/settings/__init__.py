import os

file_path = os.path.normpath(os.path.abspath(__file__))
file_path_list = file_path.split(os.sep)

# selector
which = 1

# files

while file_path_list[-1] != 'sherbot':
    del file_path_list[-1]

DIR_PATH = os.sep.join(file_path_list) + '/'

LOG_PATH_FILE = DIR_PATH + 'log.txt'

NLU_DATA_PATH = DIR_PATH + ('resources/nlu/data/nlu_data.md' if which else 'resources/nlu/data/nlu_data_b.md')

NLU_MODEL_PATH = DIR_PATH + 'resources/nlu/models/default/nlu_model'

NLU_MODEL_DIR_PATH = DIR_PATH + 'resources/nlu/models'

DB_CONCEPT_PATH = DIR_PATH + ('resources/db/db_concept.json' if which else 'resources/db/db_concept_c.json')

DB_SCHEMA_PATH = DIR_PATH + ('resources/db/db_schema.json' if which else 'resources/db/db_schema_c.json')

# settings

#db

DATABASE_NAME = 'employees' if which else 'classicmodels'

# nlu

NLU_CONFIG_PIPELINE = "tensorflow_embedding"  # spacy_sklearn
NLU_CONFIG_LANGUAGE = "en"
