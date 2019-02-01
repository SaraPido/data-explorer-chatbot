def ERROR(messages):
    messages.append('Sorry, I did not get that! :(')


def FINDING_ELEMENT(messages):
    messages.append('Let me check...')


def NOTHING_FOUND(messages):
    messages.append('Nothing has been found, I am sorry!')


def ONE_RESULT_FOUND(messages):
    messages.append('Et voilà! I found 1 result:')


def N_RESULTS_FOUND(messages, count):
    messages.append('Et voilà! I found {} results:'.format(count))


def SELECT_FOR_INFO(messages, show_more=False):
    str_show_more = ' or click the last button to see more' if show_more else ''
    messages.append('Select the one you are interested in' + str_show_more + '.')


def INTRODUCE_ELEMENT_TO_SHOW(messages, element_name):
    messages.append('Here is what I know about this {}:'.format(element_name))


def EMPTY_CONTEXT_LIST(messages):
    messages.append('What are we talking about? No element has been registered yet!')


def SHOW_CURRENT_ACTION_NAME_CONTEXT(messages, action_name):
    messages.append(action_name)


def CONTEXT_LIST_RESET(messages):
    messages.append('The context has been reset!')


def SHOW_CONTEXT_INFO(messages):
    messages.append('Click a button to go back in the context\n'
                    'Currently the context of the conversation is the following:')
