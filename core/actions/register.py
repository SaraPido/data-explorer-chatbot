from rasa_core_sdk import Action
from server.core.actions import handlers


class A1(Action):
    def name(self):
        return 'action_find_teacher_by_word'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_find_element_by_word(self, dispatcher, tracker, domain, 'teacher')


class A2(Action):
    def name(self):
        return 'action_find_lesson_by_word'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_find_element_by_word(self, dispatcher, tracker, domain, 'lesson')


class A3(Action):
    def name(self):
        return 'action_find_class_by_word'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_find_element_by_word(self, dispatcher, tracker, domain, 'class')


''' view table properties '''


class A4(Action):
    def name(self):
        return 'action_view_element_id'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_view_element_id(self, dispatcher, tracker, domain, 'id')


class A5(Action):
    def name(self):
        return 'action_view_element_telephone'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_view_element_id(self, dispatcher, tracker, domain, 'telephone')


class A6(Action):
    def name(self):
        return 'action_view_element_email'

    def run(self, dispatcher, tracker, domain):
        return handlers.run_action_view_element_id(self, dispatcher, tracker, domain, 'email')
