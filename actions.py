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


''' DATABSE HANDLERS '''

import mysql.connector

cnx = mysql.connector.connect(user='rasa', password='rasa', host='127.0.0.1', database='rasa_db')

def select(query):
	global cnx
	cursor = cnx.cursor()
	cursor.execute(query)
	return cursor.fetchall()

#cnx.close()


''' CONTEXT LIST HANDLERS '''

def get_element_from_context_list(element_name, context_list):
	element = next(filter(lambda el: el['type']==element_name, context_list), None)
	if element!= None:
		return element['value']
	else:
		return None

def add_element_to_context_list(element, element_name, context_list):
	context_list.append({'type':element_name, 'value':element})
	print('\n *** Element '+element_name+' has been added to the context_list ***')
	print_context_list(context_list)

def pop_element_and_leaves_from_context_list(element_name, context_list):
	size = len(context_list)
	index = next((i for i,v in enumerate(context_list) if v['type']==element_name), size)
	del context_list[index:]
	if index!= size:
		print('\n *** Element '+element_name+' and its leaves has been deleted from the context_list *** \n')

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


''' ACTIONS '''

''' Validate '''

class ActionValidateTeacherName(Action):

	def name(self):
		return 'action_validate_teacher_name'

	def run(self, dispatcher, tracker, domain):

		context_list = tracker.get_slot('context_list')

		teacher_name = next(tracker.get_latest_entity_values('teacher_name'), None)

		if teacher_name!=None:
			query = "SELECT id, name, surname FROM Teacher WHERE name = '"+teacher_name+"'"
			rows = select(query)

			if len(rows)==1:
				row = rows[0]

				#TESTING, now i am APPENDING the teacher in ANY case
				## TEST: now I just want to empty the context_list if there is already a teacher
				## because I assume I am "exiting" the contest
				pop_element_and_leaves_from_context_list('teacher',context_list)
				add_element_to_context_list({'id':row[0], 'name':row[1], 'surname':row[2]},'teacher', context_list)

				return [
					SlotSet('found_name', True),
					SlotSet('context_list', context_list)
				]

			else:
				print('I received invalid name: '+teacher_name)

		else:

			print('\n ** NO entity teacher_name has been extracted :( **\n')

			teacher = get_element_from_context_list('teacher', context_list)
			if teacher!=None:

				pop_element_and_leaves_from_context_list('teacher',context_list)
				add_element_to_context_list('teacher', teacher, context_list)


				return [
					SlotSet('teacher_name', teacher['name']),
					SlotSet('found_name', True),
					SlotSet('context_list', context_list)
				]

		return [SlotSet('found_name', False)]


class ActionValidateLessonName(Action):

	def name(self):
		return 'action_validate_lesson_name'

	def run(self, dispatcher, tracker, domain):

		lesson_name = next(tracker.get_latest_entity_values('lesson_name'), None)

		context_list = tracker.get_slot('context_list')

		if lesson_name!=None:
			lesson_list = get_element_from_context_list('lesson_list', context_list)

			if lesson_list!=None:
				lesson = next(filter(lambda l: l['name']==lesson_name, lesson_list), None)
				if lesson!=None:

					pop_element_and_leaves_from_context_list('lesson',context_list)
					add_element_to_context_list(lesson,'lesson', context_list)

					return [
						SlotSet("found_name", True),
						SlotSet('context_list', context_list)
					]
		else:

			lesson = get_element_from_context_list('lesson', context_list)

			print_context_list(context_list)
			if lesson!=None:

				pop_element_and_leaves_from_context_list('lesson',context_list)
				add_element_to_context_list(lesson,'lesson', context_list)

				print('\nI will return found_name == True...\n')

				return [
					SlotSet("lesson_name", lesson['name']),
					SlotSet('found_name', True),
					SlotSet('context_list', context_list)
				]

		return [SlotSet('found_name', False)]


''' Getters '''

class ActionGetLessonsOfTeacherName(Action):

	def name(self):
		return 'action_get_lessons_of_teacher_name'

	def run(self, dispatcher, tracker, domain):

		context_list = tracker.get_slot('context_list')
		teacher = get_element_from_context_list('teacher', context_list)
		teacher_id = teacher['id']

		query = "SELECT * FROM Lesson WHERE teacher_id = '"+str(teacher_id)+"'"
		rows = select(query)

		#from a list of tuples to a list of dictionaries
		lesson_list = list(map(lambda r: {'id':r[0], 'name':r[1]} , rows))

		pop_element_and_leaves_from_context_list('lesson_list',context_list)

		add_element_to_context_list(lesson_list, 'lesson_list', context_list)

		#What if only one lesson is returned? can i jump the step of the list? let us see..
		if len(lesson_list) == 1:
			add_element_to_context_list(lesson_list[0], 'lesson', context_list)

		return [
			SlotSet('context_list',context_list),
			SlotSet('lesson_name_list','\n'.join(map(lambda l:l['name'],lesson_list)))
		]

class ActionGetTimetablesOfLessonName(Action):

	def name(self):
		return 'action_get_timetables_of_lesson_name'

	def run(self, dispatcher, tracker, domain):

		context_list = tracker.get_slot('context_list')
		lesson = get_element_from_context_list('lesson',context_list)
		lesson_id = lesson['id']

		query = "SELECT * FROM Timetable WHERE lesson_id = '"+str(lesson_id)+"'"
		rows = select(query)

		timetable_list = list(map(lambda r: {'id':r[0], 'day':r[1], 'from_time':r[2], 'to_time':r[3]} , rows))

		pop_element_and_leaves_from_context_list('timetable_list',context_list)
		add_element_to_context_list(timetable_list,'timetable_list',context_list)

		timetable_name_list = '\n'.join(map(lambda l:'{}, from {} to {}'\
							.format(l['day'],l['from_time'],l['to_time']),timetable_list))

		return [
			SlotSet('context_list', context_list),
			SlotSet('timetable_name_list', timetable_name_list)
		]

class ActionGetClassOfLessonName(Action):

	def name(self):
		return 'action_get_class_of_lesson_name'

	def run(self, dispatcher, tracker, domain):

		context_list = tracker.get_slot('context_list')
		lesson = get_element_from_context_list('lesson',context_list)
		lesson_id = lesson['id']

		query = "SELECT * FROM Class C, Lesson L WHERE \
		L.id = '"+str(lesson_id)+"' AND L.class_id = C.id"

		rows = select(query)
		r = rows[0]
		clazz = {'id':r[0], 'name':r[1]}

		pop_element_and_leaves_from_context_list('class',context_list)
		add_element_to_context_list(clazz,'class',context_list)


		return [
			SlotSet("context_list", context_list),
			SlotSet("class_name", clazz['name'])
		]
