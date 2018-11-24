'''
In order to start the actions server:
python -m rasa_core_sdk.endpoint --actions actions -p 5055
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet
from rasa_core_sdk.forms import FormAction


''' DATABASE HANDLERS '''

import mysql.connector
#import psycopg2

cnx = mysql.connector.connect(user='rasa', password='rasa', host='127.0.0.1', database='rasa_db')
#cnx = psycopg2.connect("host='localhost' dbname='rasa_db' user='rasa' password='rasa'")

def select(query):
	global cnx
	cursor = cnx.cursor()
	cursor.execute(query)
	return cursor.fetchall()

#cnx.close()


''' CONTEXT LIST HANDLERS '''

def get_element_from_context_list(element_type):
	global context_list
	element = next(filter(lambda el: el['type']==element_type, context_list), None)
	if element!= None:
		return element['value']
	else:
		return None

def add_element_to_context_list(element_type, element):
	global context_list
	context_list.append({'type':element_type, 'value':element})
	print('\n *** Element '+element_type+' has been added to the context_list ***')
	print_context_list(context_list)

def pop_element_and_leaves_from_context_list(element_type):
	global context_list
	size = len(context_list)
	index = next((i for i,v in enumerate(context_list) if v['type']==element_type), size)
	del context_list[index:]
	if index!= size:
		print('\n *** Element '+element_type+' and its leaves has been deleted from the context_list *** \n')


''' PRINTER '''

def print_context_list(lis):
	sep = ' * '
	for el in lis:
		if isinstance(el['value'],list)==False:
			print(sep + el['type'] + ': ' + str(el['value']))
		else:
			print(sep + el['type'] + ':')
			for obj in el['value']:
				print(sep + '- ' + str(obj))
	print()


### TODO: parametrize the most of it!
table_properties = [
	{'type':'teacher', 'columns':['id','name','surname'], 'id':['id'], 'word':['name','surname']},
	{'type':'lesson', 'columns':['id','name','class_id','teacher_id'], 'id':['id'], 'word':['name']},
	{'type':'class', 'columns':['id','name'], 'id':['id'], 'word':['name']}
]

''' HELPERS '''

def get_element_word_columns(element_type):
	element = next(filter(lambda el: el['type']==element_type, table_properties), None)
	return element['word']

def select_on_word(element_type, word):
	query_string = "SELECT * FROM "+element_type.capitalize()+" "
	columns = get_element_word_columns(element_type)
	#### TODO: Review this part...
	# e.g. "SELECT * FROM Teacher WHERE name='"+word+"' OR surname='"+word+"'"
	for i,col in enumerate(columns):
		if i == 0:
			query_string += "WHERE "
		query_string += ""+col+"='"+word+"'"
		#if not the last column
		if i!= len(columns)-1:
			query_string += " OR "
	res = select(query_string)
	if len(res)>0: return res
	else: return None

def decorate_rows(element_type, rows):
	element = next(filter(lambda el: el['type']==element_type, table_properties), None)
	if element!= None:
		columns = element['columns']
		return list(map(lambda r: dict(zip(columns, r)), rows))

def find_element_by_word(element_type, word):
	rows = select_on_word(element_type, word)
	if rows!=None:
		element_list = decorate_rows(element_type, rows)
		add_element_to_context_list(element_type+'_list', element_list)
		if len(element_list)==1:
			add_element_to_context_list(element_type, element_list[0])
		return element_list
	else: return None

def get_result_message(element_type, element_list):
	message = 'Results:\n'
	word_columns = get_element_word_columns(element_type)
	for i,e in enumerate(element_list):
		message += '- '
		message += ' '.join(e[x] for x in word_columns)
		if i == len(e)-1: message += '\n'
	return message

def reset_context_list():
	global context_list
	context_list = list()

''' ACTIONS '''

def run_action_find_element_by_word(self, dispatcher, tracker, domain, element_type):

	word = next(tracker.get_latest_entity_values('word'), None)

	# when a "find" action gets called, the context list is reset
	reset_context_list()

	if word != None:

		element_list = find_element_by_word(element_type, word)

		if element_list==None:
			message = 'Nothing has been found with: '+ word
		else:
			message = get_result_message(element_type, element_list)

	else:
		message = "No word entity has been received..."

	dispatcher.utter_message(message)

	return []

class A1(Action):
	def name(self):
		return 'action_find_teacher_by_word'
	def run(self, dispatcher, tracker, domain):
		return run_action_find_element_by_word(self, dispatcher, tracker, domain, 'teacher')

class A2(Action):
	def name(self):
		return 'action_find_lesson_by_word'
	def run(self, dispatcher, tracker, domain):
		return run_action_find_element_by_word(self, dispatcher, tracker, domain, 'lesson')

class A3(Action):
	def name(self):
		return 'action_find_class_by_word'
	def run(self, dispatcher, tracker, domain):
		return run_action_find_element_by_word(self, dispatcher, tracker, domain, 'class')

# context_list
reset_context_list()

# eof
