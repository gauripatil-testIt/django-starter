from django.test import TestCase

from core.models import Task


class TaskModelTests(TestCase):
    def test_str_returns_title(self):
        task = Task(title='Write tests')
        self.assertEqual(str(task), 'Write tests')

    def test_default_status_is_todo(self):
        task = Task(title='Write tests')
        self.assertEqual(task.status, 'todo')
