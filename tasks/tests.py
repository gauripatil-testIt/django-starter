from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskListFilterSortTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='owner',
            password='test-password-123',
        )
        self.other_user = user_model.objects.create_user(
            username='other',
            password='test-password-123',
        )
        self.client.force_login(self.user)

        today = date.today()
        self.alpha = Task.objects.create(
            owner=self.user,
            title='Alpha report',
            status=Task.Status.TODO,
            due_date=today + timedelta(days=3),
        )
        self.beta = Task.objects.create(
            owner=self.user,
            title='Beta todo',
            status=Task.Status.TODO,
            due_date=today + timedelta(days=1),
        )
        self.doing = Task.objects.create(
            owner=self.user,
            title='Doing task',
            status=Task.Status.DOING,
            due_date=today + timedelta(days=2),
        )
        self.done = Task.objects.create(
            owner=self.user,
            title='Done task',
            status=Task.Status.DONE,
            due_date=today + timedelta(days=4),
        )
        self.undated = Task.objects.create(
            owner=self.user,
            title='Undated task',
            status=Task.Status.TODO,
        )
        self.other = Task.objects.create(
            owner=self.other_user,
            title='Other user todo',
            status=Task.Status.TODO,
            due_date=today,
        )

    def assert_task_order(self, response, titles):
        html = response.content.decode()
        positions = []
        for title in titles:
            self.assertIn(title, html, f'{title!r} should be rendered')
            positions.append(html.index(title))
        self.assertEqual(positions, sorted(positions))

    def test_status_filter_lists_only_matching(self):
        response = self.client.get(reverse('task_list'), {'status': 'todo'})
        self.assertEqual(response.status_code, 200)
        for title in ('Alpha report', 'Beta todo', 'Undated task'):
            self.assertContains(response, title)
        self.assertNotContains(response, 'Doing task')
        self.assertNotContains(response, 'Done task')
        self.assertNotContains(response, 'Other user todo')

    def test_search_is_case_insensitive(self):
        response = self.client.get(reverse('task_list'), {'q': 'ALPHA'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha report')
        self.assertNotContains(response, 'Beta todo')
        self.assertNotContains(response, 'Doing task')

    def test_default_sort_is_due_date_ascending(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assert_task_order(
            response,
            ['Beta todo', 'Doing task', 'Alpha report', 'Done task', 'Undated task'],
        )

    def test_sort_desc_reverses_due_date_order(self):
        response = self.client.get(reverse('task_list'), {'sort': 'desc'})
        self.assertEqual(response.status_code, 200)
        self.assert_task_order(
            response,
            ['Done task', 'Alpha report', 'Doing task', 'Beta todo', 'Undated task'],
        )

    def test_tasks_without_due_date_are_last_in_both_directions(self):
        dated_titles = ['Beta todo', 'Doing task', 'Alpha report', 'Done task']
        for query in ({}, {'sort': 'desc'}):
            response = self.client.get(reverse('task_list'), query)
            self.assertEqual(response.status_code, 200)
            html = response.content.decode()
            undated_pos = html.index('Undated task')
            for title in dated_titles:
                self.assertLess(
                    html.index(title),
                    undated_pos,
                    f'{title!r} should come before the undated task',
                )

    def test_combination_is_reflected_in_query_string_and_reproducible(self):
        url = reverse('task_list') + '?status=todo&q=beta&sort=desc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beta todo')
        self.assertNotContains(response, 'Alpha report')

        toggle_url = reverse('task_list') + '?sort=asc&status=todo&q=beta'
        escaped_toggle = toggle_url.replace('&', '&amp;')
        self.assertContains(response, f'href="{escaped_toggle}"')

        repeated = self.client.get(url)
        self.assertEqual(response.content, repeated.content)

    def test_controls_show_current_values(self):
        response = self.client.get(
            reverse('task_list'),
            {'status': 'doing', 'q': 'alpha', 'sort': 'desc'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="doing" selected>Doing</option>')
        self.assertContains(response, 'name="q" value="alpha"')
        self.assertContains(response, 'name="sort" value="desc"')
        self.assertContains(response, 'Descending')
        self.assertNotContains(response, 'Ascending')

    def test_all_statuses_selected_by_default(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="" selected>All statuses</option>')

    def test_no_matches_shows_message_and_clear_link(self):
        response = self.client.get(reverse('task_list'), {'q': 'zzz'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tasks match your filters')
        self.assertContains(response, 'Clear filters')
        self.assertContains(response, f'href="{reverse("task_list")}"')
        self.assertNotContains(response, 'No tasks yet')

    def test_list_excludes_other_users_tasks(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha report')
        self.assertNotContains(response, 'Other user todo')
