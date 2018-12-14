def ERROR(messages):
    messages.append('Sorry, I did not get that! :(')


def ELEMENT_TYPE_NOT_FINDABLE_BY_WORD(messages, el_type):
    messages.append('I am sorry, but you cannot find elements of type "{}" by word'.format(el_type))


def FIND_BY_WORD(messages, el_type, word):
    messages.append('If I am right, you are looking for...\n'
                    'Element: {}\n'
                    'By word: "{}"\n'
                    'Let me check if it is present the database...\n'.format(el_type.upper(), word))


def NOTHING_FOUND(messages):
    messages.append('Nothing has been found, I am sorry!')


def ONE_RESULT_FOUND(messages):
    messages.append('One result has been found!')


def COUNT_RESULTS_FOUND(messages, count):
    messages.append('{} results have been found!'.format(count))


def SELECT_FOR_INFO(messages):
    messages.append('If you want more information, select one!')


def ONLY_COUNT_DISPLAYED(messages, count):
    messages.append('Only {} will be displayed here!'.format(count))


def EMPTY_CONTEXT_LIST(messages):
    messages.append('What are we talking about? No element has been registered yet!')
