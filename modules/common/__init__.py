def get_dict(*variables):
    return {var_name(s=s): s for s in variables}


def var_name(**variables):
    return list(variables.keys())[0]
