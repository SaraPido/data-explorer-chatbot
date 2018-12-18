import json
import logging
import re

import sqlparse
from mysql import connector

from modules.settings import DATABASE_NAME, DB_SCHEMA_PATH

logger = logging.getLogger(__name__)

db_schema = None
connection = None


def connect():
    global connection
    logger.info('Connecting to the database...')
    connection = connector.connect(user='root', password='admin', host='127.0.0.1', database=DATABASE_NAME)
    logger.info('Connection succeeded!')
    # cnx.close()


def load_db_schema():
    global db_schema
    with open(DB_SCHEMA_PATH) as f:
        db_schema = json.load(f)
    logger.info('Database schema file has been loaded!')


def query_select(query, t=None):
    logger.info('Executing query...')
    logger.info('Query: "{}"'.format(query))
    if t:
        logger.info('Tuple: {}'.format(t))
    cursor = connection.cursor()
    cursor.execute(query, t)
    return cursor.fetchall()


def get_table_schema_from_name(table_name):
    for table_schema in db_schema:
        if table_schema['table_name'] == table_name:
            return table_schema
    return None


def decorate_rows(rows, table_name):
    element = next(filter(lambda el: el['table_name'] == table_name, db_schema), None)
    if element:
        columns = element['column_list']
        return list(map(lambda r: dict(zip(columns, r)), rows))
    else:
        pass  # todo: error/exception


def query_select_on_word(table_name, word_column_list, word):

    query_string = "SELECT * FROM {} ".format(table_name)
    query_string += "WHERE "
    query_string += " OR ".join(["{}=%s".format(w_col) for w_col in word_column_list])

    tup = tuple([word] * len(word_column_list))

    rows = query_select(query_string, tup)

    return decorate_rows(rows, table_name)


def join_one_to_many(element, from_table_name, to_table_name):
    from_schema = get_table_schema_from_name(from_table_name)
    to_schema = get_table_schema_from_name(to_table_name)

    query_string = "SELECT "
    query_string += ", ".join(["Z.{}".format(col) for col in to_schema['column_list']])
    query_string += " "
    query_string += "FROM {} A, {} Z ".format(from_schema['table_name'], to_schema['table_name'])
    query_string += "WHERE "
    query_string += " AND ".join(["A.{}=Z.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(from_schema, to_schema)])
    query_string += " AND "
    query_string += " AND ".join(['A.{}=%s'.format(primary, element[primary])
                                 for primary in from_schema['primary_key_list']])

    tup = tuple([element[primary] for primary in from_schema['primary_key_list']])

    rows = query_select(query_string, tup)

    return decorate_rows(rows, to_table_name)


def join_many_to_many(element, from_table_name, to_table_name, by_table_name):
    from_schema = get_table_schema_from_name(from_table_name)
    to_schema = get_table_schema_from_name(to_table_name)
    by_schema = get_table_schema_from_name(by_table_name)

    query_string = "SELECT "
    # relation/by columns
    query_string += ", ".join(["Z.{}".format(col)
                               for col in to_schema['column_list']]
                              +
                              ["Y.{}".format(col)
                               for col in by_schema['column_list']])
    query_string += " "
    query_string += "FROM {} A, {} Y, {} Z ".format(from_table_name, by_table_name, to_table_name)
    query_string += "WHERE "
    query_string += " AND ".join(["A.{}=Y.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(from_schema, by_schema)])

    query_string += " AND "
    query_string += " AND ".join(["Y.{}=Z.{}".format(p[0], p[1])
                                 for p in get_paired_reference_key_list(by_schema, to_schema)])

    query_string += " AND "
    query_string += " AND ".join(['A.{}=%s'.format(primary, element[primary])
                                 for primary in from_schema['primary_key_list']])

    tup = tuple([element[primary] for primary in from_schema['primary_key_list']])

    rows = query_select(query_string, tup)

    first_type = decorate_rows(rows, to_table_name)
    index = len(first_type)
    second_type = decorate_rows([r[index:] for r in rows], by_table_name)

    return first_type, second_type


def get_paired_reference_key_list(from_schema, to_schema):
    from_property_list = from_schema['foreign_property_list']
    to_property_list = to_schema['foreign_property_list']
    if from_property_list:
        for prop in from_property_list:
            if prop['reference_table_name'] == to_schema['table_name']:
                return zip(prop['foreign_key_list'], prop['reference_key_list'])
    if to_property_list:
        for prop in to_property_list:
            if prop['reference_table_name'] == from_schema['table_name']:
                return zip(prop['reference_key_list'], prop['foreign_key_list'])
    return None


# parser methods

def extract_table_name_from_tokens(tokens):
    table_name = next(t for t in tokens if isinstance(t, sqlparse.sql.Identifier))
    table_name_str = str(table_name)
    # removes the ' '
    return re.match(r'[^\w]*(\w*)', table_name_str).group(1)


def extract_lines_from_tokens(tokens):
    par = next(t for t in tokens if isinstance(t, sqlparse.sql.Parenthesis))
    par_str = str(par)[1:-1]  # removes the ( )
    # split on commas if not in parentheses, using negative lookahead
    return re.split(r',(?![^()]*\))', par_str, re.DOTALL)


def extract_ddl_list(str):
    string_list = str.split(',')
    return list(re.match(r'[^\w]*(\w*)', s).group(1) for s in string_list)

# def extract_and_correct_keys(raw):


if __name__ == '__main__':

    schema = list()

    # with open('../../resources/db/employees.sql') as f:
    # with open('../../resources/db/rasa_db.sql') as f:
    with open('../../resources/db/mysqlsampledatabase.sql') as f:
        raw = f.read()

    for s in sqlparse.split(raw):
        for parsed in sqlparse.parse(s):
            if parsed.get_type() == 'CREATE' and any(t.match(sqlparse.tokens.Keyword, 'TABLE')
                                                     for t in parsed.tokens
                                                     if isinstance(t, sqlparse.sql.Token)):

                    table_dict = dict()
                    table_dict['table_name'] = extract_table_name_from_tokens(parsed.tokens)
                    table_dict['column_list'] = []
                    table_dict['primary_key_list'] = []
                    table_dict['foreign_property_list'] = []

                    lines = extract_lines_from_tokens(parsed.tokens)

                    for l in lines:

                        match_column = re.match(r'[^\w]*(\w*)', l, re.DOTALL)
                        match_primary = re.match(r'.*PRIMARY KEY[^\(]*\((.*)\)', l, re.DOTALL)
                        match_constraint = re.match(r'.*FOREIGN KEY[^\(]*\((.*)\).*REFERENCES[^\w]*(\w*)[^\(]*\((.*)\)',
                                                    l, re.DOTALL)
                        if match_column:
                            if match_column.group(1) not in ['PRIMARY', 'FOREIGN', 'UNIQUE', 'KEY', 'CONSTRAINT']:
                                table_dict['column_list'].append(match_column.group(1))
                        if match_primary:
                            table_dict['primary_key_list'].extend(extract_ddl_list(match_primary.group(1)))
                        if match_constraint:
                            foreign_property_dict = dict()
                            foreign_property_dict['foreign_key_list'] = extract_ddl_list(match_constraint.group(1))
                            foreign_property_dict['reference_table_name'] = match_constraint.group(2)
                            foreign_property_dict['reference_key_list'] = extract_ddl_list(match_constraint.group(3))
                            table_dict['foreign_property_list'].append(foreign_property_dict)

                    schema.append(table_dict)
                    for fp in table_dict['foreign_property_list']:
                        print('{} - {}'.format(table_dict['table_name'], fp['reference_table_name']))

    with open('../../resources/db/db_schema_c.json', 'w') as f:
        json.dump(schema, f, indent=4)

