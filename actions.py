
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

conn = create_connection('./data/db/test.db')

def select_all_rows(table_name):
	global conn
	cur = conn.cursor()
	query = 'SELECT * FROM ' + table_name
	cur.execute(query)
	rows = cur.fetchall()
	return rows

class ActionViewSpecificTable(Action):

	def name(self):
		return 'action_view_specific_table'

	def run(self, dispatcher, tracker, domain):
		table_name = tracker.get_slot('table_name')
		response = 'Here all the rows of the table '+ table_name +': ...\n'
		rows = select_all_rows(table_name)
		for row in rows:
			response = response + str(row) + '\n'
		dispatcher.utter_message(response)
		return []
