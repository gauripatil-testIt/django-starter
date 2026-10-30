from config import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from core.models import Task
from core.services import send_task_assigned_email


class SendTaskAssignedEmailTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123',
        )
        self.assignee = get_user_model().objects.create_user(
            username='assignee',
            email='assignee@example.com',
            password='testpass123',
        )

    def test_assignment_sends_exactly_one_email_with_title_and_relative_link(self):
        task = Task.objects.create(
            title='Fix the bug',
            owner=self.owner,
            assignee=self.assignee,
        )

        sent = send_task_assigned_email(task)

        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [self.assignee.email])
        self.assertEqual(message.subject, 'Task assigned: Fix the bug')
        self.assertIn('Fix the bug', message.body)
        self.assertIn(f'/tasks/{task.pk}/', message.body)

    def test_no_email_when_assignee_unchanged(self):
        task = Task.objects.create(
            title='Fix the bug',
            owner=self.owner,
            assignee=self.assignee,
        )

        sent = send_task_assigned_email(task, previous_assignee=self.assignee)

        self.assertEqual(sent, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_on_self_assignment(self):
        task = Task.objects.create(
            title='Fix the bug',
            owner=self.owner,
            assignee=self.owner,
        )

        sent = send_task_assigned_email(task)

        self.assertEqual(sent, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_dev_mailer_is_console_backend(self):
        self.assertEqual(
            settings.MAILERS['default']['BACKEND'],
            'django.core.mail.backends.console.EmailBackend',
        )
