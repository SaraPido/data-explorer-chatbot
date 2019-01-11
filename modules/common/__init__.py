def get_dict(*variables):
    return {var_name(s=s): s for s in variables}


def var_name(**variables):
    return list(variables.keys())[0]


KEY_QUERY = 'query'
KEY_QUERY_STRING = 'q_string'
KEY_QUERY_TUPLE = 'q_tuple'
KEY_ACTION_DESCRIPTION = 'action_description'
KEY_VALUE = 'value'
KEY_BY_VALUE = 'by_value'
KEY_REAL_VALUE_LENGTH = 'real_value_length'

