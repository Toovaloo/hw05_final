from django.test import TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    # Создать фикстуры клиента и 13 тестовых записей
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем записи в базе данных
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='piclover'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание тестовой группы'
        )
        a_list = []
        for i in range(1, 14):
            i = Post(text='Тестовый текст',
                     author=cls.author,
                     group=cls.group)
            a_list.append(i)
        Post.objects.bulk_create(a_list)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
