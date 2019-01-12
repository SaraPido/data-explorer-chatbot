def ERROR(messages):
    messages.append('Sorry, I did not get that! :(')


def ELEMENT_NOT_FINDABLE_BY_WORD(messages, element_name):
    messages.append('I am sorry, but you cannot find elements "{}" by word'.format(element_name))


def ELEMENT_NOT_FINDABLE_BY_NUMBER(messages, element_name):
    messages.append('I am sorry, but you cannot find elements "{}" by number'.format(element_name))


def FIND_BY_WORD(messages, element_name, word):
    messages.append('If I am right, you are looking for...\n'
                    'Element: {}\n'
                    'By word: "{}"\n'
                    'Let me check if it is present the database...\n'.format(element_name.upper(), word))


def FIND_BY_NUMBER(messages, element_name, number):
    messages.append('If I am right, you are looking for...\n'
                    'Element: {}\n'
                    'By number: "{}"\n'
                    'Let me check if it is present the database...\n'.format(element_name.upper(), number))


def NOTHING_FOUND(messages):
    messages.append('Nothing has been found, I am sorry!')


def ONE_RESULT_FOUND(messages):
    messages.append('One result has been found!')


def N_RESULTS_FOUND(messages, count):
    messages.append('{} results have been found!'.format(count))


def SELECT_FOR_INFO(messages):
    messages.append('If you want more information, select one!')


def ONLY_N_DISPLAYED(messages, count):
    messages.append('Only {} will be displayed here!'.format(count))


def EMPTY_CONTEXT_LIST(messages):
    messages.append('What are we talking about? No element has been registered yet!')


def SHOW_CURRENT_ACTION_NAME_CONTEXT(messages, action_name):
    messages.append(action_name)


def CONTEXT_LIST_RESET(messages):
    messages.append('The context has been reset!')


def SHOW_CONTEXT_INFO(messages):
    messages.append('Click a button to go back in the context\n'
                    'Currently the context of the conversation is the following:')
