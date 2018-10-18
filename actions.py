'''
In order to start the actions server:
python -m rasa_core_sdk.endpoint --actions actions -p 5055
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
	try:
		return sqlite3.connect(db_file)
	except Error as e:
		print(e)
		return None

conn = create_connection('./db/test.db')

def select_all_rows(table_name):
	global conn
	cur = conn.cursor()
	query = 'SELECT * FROM ' + table_name
	cur.execute(query)
	rows = cur.fetchall()
	return rows

class ActionViewAllTables(Action):

	def name(self):
		return 'action_view_all_tables'

	def run(self, dispatcher, tracker, domain):
		response = 'Which table to you want to look at?'
		#here the action should retrieve the NAMES of the tables
		buttons = [
			{'title':'Projects', 'payload':'/choose{"table_name": "Projects"}'},
			{'title':'Tasks', 'payload':'/choose{"table_name": "Tasks"}'}
		]
		dispatcher.utter_button_message(response, buttons)
		return []

class ActionViewSpecificTable(Action):

	def name(self):
		return 'action_view_specific_table'

	def run(self, dispatcher, tracker, domain):
		table_name = tracker.get_slot('table_name')
		response = 'Here all the rows of the table '+ table_name +':'
		rows = list(select_all_rows(table_name))
		for row in rows:
			response = response + '\n' + str(row)
		dispatcher.utter_message(response)
		return []

class ActionAskWhichAttribute(Action):

	def name(self):
		return 'action_ask_which_attribute'

	def run(self, dispatcher, tracker, domain):
		table_name = tracker.get_slot('table_name')
		response = 'So you want to filter the results of '+table_name+'. By which attribute?'
		global conn
		cur = conn.cursor()
		query = 'SELECT * FROM ' + table_name
		cur.execute(query)
		names = [d[0] for d in cur.description]
		#here the action should retrieve the possible attributes
		buttons = list()
		for n in names:
			buttons.append({'title':n, 'payload':'/choose{"attribute_name": "'+n+'"}'})
		dispatcher.utter_message(response)
		buttons_list = [buttons[i:i+3] for i in range(0,len(buttons),3)] #max 3 buttons at a time
		for b_element in buttons_list:
			dispatcher.utter_button_message('',b_element)
		return []

class ActionFilterByAttribute(Action):

	def name(self):
		return 'action_filter_table_by_attribute'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message('Good job')
		return []
