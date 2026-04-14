from django.contrib.auth import get_user_model
from django.test import TestCase
from pytils.translit import slugify


User = get_user_model()
# Импортируем модель, чтобы работать с ней в тестах.
from notes.models import Note


# Создаём тестовый класс с произвольным названием, наследуем его от TestCase.
class TestNotes(TestCase):
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'
    SLUG = 'Слаг'

    # В методе класса setUpTestData создаём тестовые объекты.
    # Оборачиваем метод соответствующим декоратором.
    @classmethod
    def setUpTestData(cls):
        # Стандартным методом Django ORM create() создаём объект класса.
        # Присваиваем объект атрибуту класса: назовём его news.
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author
        )

    def setUp(self):
        self.client.force_login(self.author)

    # Проверим, что объект действительно был создан.
    def test_successful_creation(self):
        # При помощи обычного ORM-метода посчитаем количество записей в базе.
        note_count = Note.objects.count()
        # Сравним полученное число с единицей.
        self.assertEqual(note_count, 1)

    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        self.assertEqual(self.note.title, self.TITLE)

    def test_slug(self):
        self.assertEqual(self.note.slug, slugify(self.TITLE))
