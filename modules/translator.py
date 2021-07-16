"""
This module takes in input the mapping (concept) of the db and generates the chatito file
"""
import random

from modules.database import resolver, broker
from settings import CHATITO_TEMPLATE_PATH, CHATITO_MODEL_PATH

if __name__ == "__main__":

    resolver.load_db_concept()
    db_concept = resolver.db_concept

    broker.load_db_schema()
    broker.test_connection()

    whole_text_more_info_find = ""
    whole_text_more_info_filter = ""
    whole_text_find = ""
    whole_text_filter = ""

    whole_element_text = ""
    whole_attribute_text = ""
    whole_example_type_text = ""

    idx_e = 1
    idx_e_alias = 0
    idx_tot = 0

    for e in db_concept:
        idx_tot += 1

        if e.get('type') == 'primary':
            tab_name_primary = e.get("table_name")

            whole_text_more_info_find += f"    ~[show?] ~[more_info_find] @[el_{tab_name_primary}]\n"
            whole_text_more_info_filter += f"    ~[show?] ~[more_info_filter] @[el_{tab_name_primary}]\n"

            element_text = f"@[el_{tab_name_primary}]\n" \
                           "    "
            element_text += "\n    ".join([e.get('element_name')] + e.get('aliases', []))
            whole_element_text += element_text + "\n\n"

            idx_e_alias += 1 + len(e.get('aliases', []))

            idx_a = 1
            for a in e.get('attributes', []):
                att_name = a.get('name')
                att_type = a.get('type')
                tab_name = e.get("table_name") if not a.get('by') else a.get('by')[-1].get('to_table_name')
                idx_tot += 1

                if a.get('keyword'):

                    id_kw = 1

                    for kw in a.get('keyword'):

                        formated_kw = kw.format(f"@[{att_type}_{tab_name}_{att_name}]")

                        attribute_text = f"~[attr_{tab_name}_{att_name}_{id_kw}]\n" \
                                         f"    {formated_kw}"
                        whole_attribute_text += attribute_text + "\n\n"
                        id_kw += 1


                example_type_text = f"@[{att_type}_{tab_name}_{att_name}]\n"

                for col in a.get('columns', []):
                    q_string = "SELECT distinct {} FROM {}".format(col,
                                                          tab_name
                                                          if not a.get('by') else
                                                          a.get('by')[-1].get('to_table_name'))
                    res = list(broker.execute_query_select(q_string))
                    if res:
                        for r in res[:20]:  # max 20 examples each
                            if r[0]:
                                idx_tot += 1
                                str_list = str(r[0]).split()

                                from_idx = random.randint(0, len(str_list) - 1)
                                to_idx = random.randint(from_idx + 1, len(str_list))

                                words = str_list[from_idx: to_idx]
                                words[-1] = words[-1].rstrip('\'\"-,.:;!?')

                                example_type_text += "    " + " ".join(words)  # assuming 4 words are too much

                                example_type_text += "\n"

                #  print(example_type_text)

                whole_example_type_text += example_type_text + "\n"

                text = ""

                if a.get('keyword'):

                    id_kw = 1
                    for kw in a.get('keyword'):
                        text += f"~[attr_{tab_name}_{att_name}_{id_kw}] "

                        if a.get('type') == 'num':  # use nlu.ENTITY_ATTR?
                            text += '@[op_num?] '
                        id_kw += 1

                        #text += "@[{}_{}_{}]".format(a.get('type'), idx_e, idx_a)

                        whole_text_find += f"    ~[find] @[el_{tab_name_primary}] " + text + "\n"
                        whole_text_filter += "    ~[filter] ~[those?] " + text + "\n"

                idx_a += 1

            idx_e += 1

    idx_tot = min(idx_tot, 400)  # max training set

    #  prepending here...
    testing = max(1, idx_e_alias*2 // 5)

    whole_text_more_info_find = "%[more_info_find]('training': '{}', 'testing': '{}')\n{}"\
        .format(idx_e_alias*2 - idx_e_alias*2 // 5, testing, whole_text_more_info_find)  # 1:4 proportion

    whole_text_more_info_filter = "%[more_info_filter]('training': '{}', 'testing': '{}')\n{}" \
        .format(idx_e_alias*2 - idx_e_alias*2 // 5, testing, whole_text_more_info_filter)  # 1:4 proportion


    testing = max(1, idx_tot // 5)

    whole_text_find = "%[find_el_by_attr]('training': '{}', 'testing': '{}')\n{}" \
        .format(idx_tot - idx_tot // 5, testing, whole_text_find)  # 1:4 proportion

    whole_text_filter = "%[filter_el_by_attr]('training': '{}', 'testing': '{}')\n{}"\
        .format(idx_tot - idx_tot // 5, testing, whole_text_filter)  # 1:4 proportion

    final_text = "\n" + "\n".join([whole_element_text, whole_attribute_text, whole_example_type_text,
                                   whole_text_find, whole_text_filter,
                                   whole_text_more_info_find, whole_text_more_info_filter])

    with open(CHATITO_TEMPLATE_PATH, 'r') as f:
        template = f.read()
        final_text = template + final_text
        with open(CHATITO_MODEL_PATH, 'w') as f2:
            f2.write(final_text)
