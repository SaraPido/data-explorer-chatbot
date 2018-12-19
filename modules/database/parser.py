
# parser methods
import json
import re

import sqlparse


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
