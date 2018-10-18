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
		response = 'Which table to you want to look at?\n'
		#here the action should retrieve the NAMES of the tables
		buttons = [
			{'title':'', 'payload':'/choose{"table_name": "Projects"}'},
			{'title':'', 'payload':'/choose{"table_name": "Tasks"}'}
		]
		dispatcher.utter_button_message(response, buttons)
		return []

class ActionViewSpecificTable(Action):

	def name(self):
		return 'action_view_specific_table'

	def run(self, dispatcher, tracker, domain):
		table_name = tracker.get_slot('table_name')
		response = 'Here all the rows of the table '+ table_name +':\n'
		rows = select_all_rows(table_name)
		for row in rows:
			response = response + str(row) + '\n'
		dispatcher.utter_message(response)
		return []
