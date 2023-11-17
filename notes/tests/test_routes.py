from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.user = User.objects.create(username='Пользаватель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

    def test_redirects(self):
        urls = (
            ('notes:detail', (self.note.pk, )),
            ('notes:edit', (self.note.pk, )),
            ('notes:delete', (self.note.pk, )),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                login_url = reverse('users:login')
                url = reverse(name, args=args)
                excpected_url = f'{login_url}?next={url}'

                response = self.client.get(url)

                self.assertRedirects(response, excpected_url)

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = ('notes:list', 'notes:add', 'notes:success')

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.user_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        clients_statuses = (
            (self.user_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )

        for client, status in clients_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug, ))
                    response = client.get(url)

                    self.assertEqual(response.status_code, status)
