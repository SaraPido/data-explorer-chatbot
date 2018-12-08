import json
import logging

logger = logging.getLogger(__name__)

db_schema = None


def load_db_schema(db_schema_path):
    global db_schema
    with open(db_schema_path) as f:
        db_schema = json.load(f)
    logger.info('Database schema file has been loaded!')

def join_one_to_many(element, from_table, to_table):
    query_string = "SELECT "
    query_string += ", "

    query_string += ", ".join(["B.{}".format(name) for name in to_el_properties['column_list']])
    query_string += " FROM {} A, {} B ".format(from_el_properties['table_name'],
                                               to_el_properties['table_name'])
    query_string += "WHERE "
    query_string += "A.{}=B.{} ".format(relation['from'], relation['to'])
    query_string += "and A.{}={}".format(from_el_properties['id'], element_value[from_el_properties['id']])
