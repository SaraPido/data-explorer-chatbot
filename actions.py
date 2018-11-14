'''
In order to start the actions server:
python -m rasa_core_sdk.endpoint --actions actions -p 5055
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet

import mysql.connector

cnx = mysql.connector.connect(user='rasa', password='rasa', host='127.0.0.1', database='rasa_db')

def select(query):
	global cnx
	cursor = cnx.cursor()
	cursor.execute(query)
	return cursor.fetchall()

#cnx.close()


class ActionValidateTeacherName(Action):

	def name(self):
		return 'action_validate_teacher_name'

	def run(self, dispatcher, tracker, domain):
		teacher_name = tracker.get_slot('teacher_name')
		query = "SELECT id, name, surname FROM Teacher WHERE name = '"+teacher_name+"'"
		rows = select(query)
		if len(rows)==1:
			row = rows[0]
			return [
				SlotSet("teacher_id", row[0]),
				SlotSet("found_name", teacher_name)
			]
		print('I received invalid name: '+teacher_name)
		return []

class ActionValidateLessonName(Action):

	def name(self):
		return 'action_validate_lesson_name'

	def run(self, dispatcher, tracker, domain):
		lesson_name = tracker.get_slot('lesson_name')
		lesson_list = tracker.get_slot('lesson_list')
		if lesson_list!=None and any(l['name'] == lesson_name for l in lesson_list):
			return [
				SlotSet("lesson_id", 21),
				SlotSet("found_name", lesson_name)
			]
		return []


class ActionGetLessonsOfTeacherName(Action):

	def name(self):
		return 'action_get_lessons_of_teacher_name'

	def run(self, dispatcher, tracker, domain):

		teacher_id = tracker.get_slot('teacher_id')
		query = "SELECT * FROM Lesson WHERE teacher_id = '"+str(teacher_id)+"'"
		rows = select(query)

		#from a list of tuples to a list of dictionaries
		lesson_list = list(map(lambda r: {'id':r[0], 'name':r[1]} , rows))
		print(str(lesson_list))

		return [SlotSet("lesson_list", lesson_list)]

class ActionGetTimetablesOfLessonName(Action):

	def name(self):
		return 'action_get_timetables_of_lesson_name'

	def run(self, dispatcher, tracker, domain):

		## here it should get the lesson_id from the tracker
		## and then perform the query

		return [
			SlotSet("timetable_list", [
				{'id':19,'day':'Monday', 'from':'11.30', 'to':'12.30'},
				{'id':20,'day':'Wednesday', 'from':'10.30', 'to':'11.30'},
				{'id':21,'day':'Thursday', 'from':'08.30', 'to':'10.00'},
			])
		]

class ActionGetClassOfLessonName(Action):

	def name(self):
		return 'action_get_class_of_lesson_name'

	def run(self, dispatcher, tracker, domain):

		## here it should get the lesson_id from the tracker
		## and then perform the query

		return [
			SlotSet("class_id",2),
			SlotSet("class_name", "2^A")
		]

class ActionResetFoundName(Action):
	def name(self):
		return 'action_reset_found_name'
	def run(self, dispatcher, tracker, domain):
		return [SlotSet("found_name", None)]



'''
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
		names = [d[0] for d in cur.description] #retrieving the attributes
		buttons = list()
		for n in names[:3]: #MAX 3 buttons for MESSENGER
			buttons.append({'title':n, 'payload':'/choose{"attribute_name": "'+n+'"}'})
		dispatcher.utter_button_message(response,buttons)
		return []

class ActionFilterByAttribute(Action):

	def name(self):
		return 'action_filter_table_by_attribute'

	def run(self, dispatcher, tracker, domain):
		attribute_name = tracker.get_slot('attribute_name')
		dispatcher.utter_message('Good job, you chose '+ attribute_name)
		return []
'''
