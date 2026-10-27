from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .admin import TaskAdmin
from .models import Task


class HomeViewTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')


class TaskModelTests(TestCase):
    def setUp(self):
        # Built per test rather than once per class: the cascade test deletes the
        # owner, which would leave a shared class-level fixture without a pk.
        self.owner = get_user_model().objects.create_user(
            username='taskowner',
            password='test-pass-123',
        )

    def test_str_returns_title(self):
        task = Task.objects.create(title='Write the tests', owner=self.owner)
        self.assertEqual(str(task), 'Write the tests')

    def test_status_defaults_to_todo(self):
        task = Task.objects.create(title='Defaulted task', owner=self.owner)
        self.assertEqual(task.status, 'todo')
        task.refresh_from_db()
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.status, Task.Status.TODO)

    def test_status_choices_are_exactly_todo_doing_done(self):
        self.assertEqual(
            [value for value, _label in Task.Status.choices],
            ['todo', 'doing', 'done'],
        )

        for value in ('todo', 'doing', 'done'):
            task = Task.objects.create(
                title=f'Task with status {value}',
                owner=self.owner,
                status=value,
            )
            task.refresh_from_db()
            self.assertEqual(task.status, value)

        invalid = Task(title='Task with bad status', owner=self.owner, status='archived')
        with self.assertRaises(ValidationError) as ctx:
            invalid.full_clean()
        self.assertIn('status', ctx.exception.message_dict)
        self.assertFalse(Task.objects.filter(title='Task with bad status').exists())

    def test_description_and_due_date_are_optional(self):
        task = Task.objects.create(title='Task without extras', owner=self.owner)
        task.refresh_from_db()
        self.assertEqual(task.description, '')
        self.assertIsNone(task.due_date)

    def test_deleting_owner_cascades_to_tasks(self):
        task = Task.objects.create(title='Doomed task', owner=self.owner)
        self.owner.delete()
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())


class TaskAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username='taskadmin',
            email='taskadmin@example.com',
            password='test-pass-123',
        )

    def test_task_is_registered_with_task_admin(self):
        self.assertTrue(admin.site.is_registered(Task))
        self.assertIn(Task, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Task], TaskAdmin)

    def test_task_admin_options_satisfy_acceptance_criteria(self):
        task_admin = admin.site._registry[Task]
        self.assertTrue(task_admin.list_display)
        self.assertIn('title', task_admin.list_display)
        self.assertIn('status', task_admin.list_display)
        self.assertIn('due_date', task_admin.list_display)
        self.assertIn('owner', task_admin.list_display)
        self.assertIn('created_at', task_admin.list_display)
        self.assertIn('status', task_admin.list_filter)
        self.assertIn('title', task_admin.search_fields)

    def test_changelist_lists_tasks_and_filters_by_status(self):
        self.client.force_login(self.admin_user)
        todo_task = Task.objects.create(title='Todo task', owner=self.admin_user)
        doing_task = Task.objects.create(
            title='Doing task',
            owner=self.admin_user,
            status=Task.Status.DOING,
        )

        url = reverse('admin:core_task_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, todo_task.title)
        self.assertContains(response, doing_task.title)

        response = self.client.get(url, {'status__exact': 'doing'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, doing_task.title)
        self.assertNotContains(response, todo_task.title)

        response = self.client.get(url, {'q': 'Todo task'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, todo_task.title)
        self.assertNotContains(response, doing_task.title)
