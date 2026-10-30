from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from core.models import Task


class TaskAssignmentViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123',
        )
        self.assignee = user_model.objects.create_user(
            username='assignee',
            email='assignee@example.com',
            password='testpass123',
        )
        self.new_assignee = user_model.objects.create_user(
            username='new_assignee',
            email='new_assignee@example.com',
            password='testpass123',
        )
        self.client.login(username='owner', password='testpass123')

    def _task_data(self, **overrides):
        data = {
            'title': 'Fix the bug',
            'description': 'Something is broken',
            'status': 'todo',
            'due_date': '',
            'assignee': self.assignee.pk,
        }
        data.update(overrides)
        return data

    def test_create_with_assignee_sends_exactly_one_email(self):
        response = self.client.post(reverse('task_create'), self._task_data())

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Fix the bug')
        self.assertEqual(task.owner, self.owner)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [self.assignee.email])
        self.assertEqual(message.subject, 'Task assigned: Fix the bug')
        self.assertIn('Fix the bug', message.body)
        self.assertIn(f'/tasks/{task.pk}/', message.body)

    def test_create_self_assignment_sends_no_email(self):
        self.client.post(
            reverse('task_create'),
            self._task_data(assignee=self.owner.pk),
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_edit_with_unchanged_assignee_sends_no_email(self):
        task = Task.objects.create(
            title='Fix the bug',
            owner=self.owner,
            assignee=self.assignee,
        )

        response = self.client.post(
            reverse('task_edit', args=[task.pk]),
            self._task_data(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_edit_reassign_sends_exactly_one_email_to_new_assignee(self):
        task = Task.objects.create(
            title='Fix the bug',
            owner=self.owner,
            assignee=self.assignee,
        )

        response = self.client.post(
            reverse('task_edit', args=[task.pk]),
            self._task_data(assignee=self.new_assignee.pk),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [self.new_assignee.email])
        self.assertEqual(message.subject, 'Task assigned: Fix the bug')

    def test_email_body_contains_relative_task_link(self):
        self.client.post(reverse('task_create'), self._task_data())

        task = Task.objects.get(title='Fix the bug')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f'/tasks/{task.pk}/', mail.outbox[0].body)
