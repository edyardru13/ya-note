from http import HTTPStatus

from pytils.translit import slugify

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
    ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо проходил')
        cls.other_author = User.objects.create(username='Проходил - проходи')

        cls.author_client = Client()
        cls.other_author_client = Client()

        cls.author_client.force_login(cls.author)
        cls.other_author_client.force_login(cls.other_author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.note_other_author = Note.objects.create(
            title=cls.NEW_NOTE_TITLE,
            text=cls.NEW_NOTE_TEXT,
            author=cls.other_author,
        )

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.SLUG
        }
        cls.valid_form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_SLUG
        }
        cls.form_data_without_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_user_cant_create_note_with_not_unique_slug(self):
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
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
        response = self.author_client.post(
            self.ADD_URL,
            data=self.valid_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)

        new_note = Note.objects.get(slug=self.NEW_SLUG)
        self.assertEqual(new_note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.valid_form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_notes_slug_auto_creation(self):
        notes_count_before = Note.objects.count()
        self.author_client.post(
            self.ADD_URL,
            data=self.form_data_without_slug
        )
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))

    def test_author_can_edit_own_notes_but_not_others(self):
        test_data = (
            (self.note.slug, HTTPStatus.FOUND),
            (self.note_other_author.slug, HTTPStatus.NOT_FOUND),
        )
        for slug, expected_status in test_data:
            with self.subTest(slug=slug):
                url = reverse('notes:edit', args=(slug,))
                response = self.author_client.post(
                    url,
                    data=self.valid_form_data
                )
                self.assertEqual(response.status_code, expected_status)

    def test_author_can_delete_own_notes_but_not_others(self):
        self.client.force_login(self.author)
        test_data = (
            (self.note.slug, HTTPStatus.FOUND),
            (self.note_other_author.slug, HTTPStatus.NOT_FOUND),
        )
        for slug, expected_status in test_data:
            with self.subTest(slug=slug):
                url = reverse('notes:delete', args=(slug,))
                response = self.author_client.post(url)
                self.assertEqual(response.status_code, expected_status)
