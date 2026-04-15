from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Заметчик')
        cls.list_url = reverse('notes:list')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'zametka-{index}',
                author=cls.author,
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        id_notes = [notes.id for notes in notes]
        sorted_id_notes = sorted(id_notes)
        self.assertEqual(id_notes, sorted_id_notes)
