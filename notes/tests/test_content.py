from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Заметчик')
        cls.one_more_author = User.objects.create(username='Еще один Заметчик')
        cls.list_url = reverse('notes:list')

        cls.note_author = Note.objects.create(
            title='Заметка 1',
            text='Просто текст.',
            slug='zametka-1',
            author=cls.author,
        )
        cls.note_one_more_author = Note.objects.create(
            title='Заметка 2',
            text='Просто текст.',
            slug='zametka-2',
            author=cls.one_more_author,
        )

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn('object_list', response.context)

    def test_notes_list_filtered_by_author(self):
        test_data = (
            (self.author, self.note_author, self.note_one_more_author),
            (
                self.one_more_author,
                self.note_one_more_author,
                self.note_author
            ),
        )

        for user, visible_note, hidden_note in test_data:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.list_url)
                notes = response.context['object_list']

                self.assertIn(visible_note, notes)
                self.assertNotIn(hidden_note, notes)

    def test_forms_availability(self):
        self.client.force_login(self.author)
        test_data = (
            ('notes:add', None),
            ('notes:edit', (self.note_author.slug,)),
        )
        for name, args in test_data:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
