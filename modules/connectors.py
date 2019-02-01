import telepot
from telepot.loop import MessageLoop

import time

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from modules import extractor, caller

TOKEN = '609526959:AAGSGD4czhnJigcsv1QM2WUA2BMBqlw4ho0'


# on any simple message
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if msg.get('text'):
        respond(chat_id, msg['text'])


# buttons have been clicked
def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    respond(chat_id, query_data)


def respond(chat_id, msg):
    result = execute(msg)
    keyboard = None
    if result.get('buttons'):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=b['title'], callback_data=b['payload'])]
                for b in result['buttons']
            ]
        )
    messages = result['messages']
    # all but last, telegram needs..
    for msg in messages[:-1]:
        bot.sendMessage(chat_id=chat_id, text=msg)
    if not msg:
        messages = ['[Attention, you are sending a message with no text]']
    bot.sendMessage(chat_id=chat_id, text=messages[-1], reply_markup=keyboard)

def start():
    global bot
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()


def execute(message):
    parsed_message = extractor.parse(message)
    result = caller.run_action_from_parsed_message(parsed_message)
    print('messages:\n'
          '* {}'.format(result.get('messages')))
    buttons = result.get('buttons')
    if buttons:
        print('buttons:')
        for b in buttons:
            print('* {} => {}'.format(b['title'], b['payload']))
    return result
