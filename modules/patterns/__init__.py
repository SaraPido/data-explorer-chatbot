class Response:

    def __init__(self):
        self.response_list = []

    def add_message(self, message):
        print('add message ', message)
        self.response_list.append({'type': 'message',
                                   'value': message})

    def add_messages(self, messages):
        print('add messages ', messages)
        for m in messages:
            self.add_message(m)

    def add_button(self, button):
        print('add button ', button)
        self.response_list.append({'type': 'button',
                                   'value': button})

    def add_buttons(self, buttons):
        print('add buttons ', buttons)
        for b in buttons:
            self.add_button(b)

    def isEmpty(self):
        return False if self.response_list else True

    def get_printable_string(self):
        print('get_printable_string')
        string_list = []
        print(self.response_list)
        for r in self.response_list:
            if 'type' in r:
                if r['type'] == 'message':
                    string_list.append('> {}'.format(r['value']))
                else:
                    if type(r['value']) is list:
                        for rv in r['value']:
                            string_list.append('[B] {} => {}'.format(rv['title'],
                                                                     rv['payload']))
                    else:
                        string_list.append('[B] {} => {}'.format(r['value']['title'],
                                                                 r['value']['payload']))

        return '\n'.join(string_list)

    def get_telegram_or_webchat_format(self):
        result_list = []
        buttons_tmp = []
        for r in self.response_list[::-1]:  # reversed
            if r['type'] == 'button':
                buttons_tmp.insert(0, r['value'])
            else:
                result_list.insert(0, {'message': r['value'], 'buttons': buttons_tmp})  # buttons_tmp may be None
                buttons_tmp = []
        if not result_list:
            result_list.append({'message': 'ERROR: no message', 'buttons': buttons_tmp})
        return result_list

