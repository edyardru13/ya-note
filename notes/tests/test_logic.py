from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Текст комментария 2'
    NEW_NOTE_TITLE = 'Заголовок 2'
    SLUG = 'zametka'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо проходил')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.aser = User.objects.create(username='Проходил - проходи')
        cls.aser_client = Client()
        cls.aser_client.force_login(cls.aser)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.SLUG
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_cant_create_note_with_not_unique_slug(self):
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=f'{self.SLUG}{WARNING}',
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, '/done/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.aser_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.slug, self.SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.aser_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.SLUG)
