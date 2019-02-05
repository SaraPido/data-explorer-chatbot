class Response:

    def __init__(self):
        self.response_list = []

    def add_message(self, message):
        self.response_list.append({'type': 'message',
                                   'value': message})

    def add_button(self, button):
        self.response_list.append({'type': 'button',
                                   'value': button})

    def add_buttons(self, buttons):
        for b in buttons:
            self.add_button(b)

    def get_printable_string(self):
        s = '- - -\n'
        for r in self.response_list:
            if r['type'] == 'message':
                s += r['value']
            else:
                s += '* {} => {}'.format(r['value']['title'], r['value']['payload'])
            s += '\n'
        return s + '- - -'

    def get_telegram_format(self):
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

