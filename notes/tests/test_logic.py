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
    NEW_SLUG = 'zametka-2'

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
        cls.new_form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_SLUG
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_user_cant_create_note_with_not_unique_slug(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=f'{self.SLUG}{WARNING}',
        )
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_author_can_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.url, data=self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)

        new_note = Note.objects.get(slug=self.NEW_SLUG)
        self.assertEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url, data=self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)

    
