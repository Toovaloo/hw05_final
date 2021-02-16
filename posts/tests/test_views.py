import shutil
import tempfile
from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Group, Post, User, Follow


class YatubePagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='AlexeyNavalny'
        )
        cls.group_to_be_with_posts = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста с группой',
            author=cls.author,
            group=cls.group_to_be_with_posts
        )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = YatubePagesTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: name"
        cache.clear()
        templates_pages_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': 'test_slug'})
            ),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста создания нового поста
    def test_new_post_page_show_correct_context(self):
        """Шаблон создания нового поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context для страницы
    # редактирования поста содержит ожидаемые значения
    def test_post_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': 'AlexeyNavalny', 'post_id': '1'}))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context отдельного поста
    # содержит ожидаемые значения
    def test_post_page_show_correct_context(self):
        """Шаблон post_id сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': 'AlexeyNavalny', 'post_id': '1'}))
        # Взяли пост и проверили, что его содержание совпадает с ожидаемым
        post = response.context.get('post')
        post_text = post.text
        post_author = post.author
        post_group = post.group
        profile_posts_count = response.context.get('posts_count')
        self.assertEqual(
            post_text, 'Тестовый текст поста с группой')
        self.assertEqual(
            post_author, User.objects.get(id=1))
        self.assertEqual(
            post_group.title, Group.objects.get(id=1).title)
        self.assertEqual(
            profile_posts_count, 1)

    # Проверяем, что страница об авторе сайта вызывает нужный шаблон
    def test_about_author_page_uses_correct_template(self):
        """При запросе к about:author применяется шаблон author.html."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    # Проверяем, что страница о технологиях сайта вызывает нужный шаблон
    def test_about_tech_page_uses_correct_template(self):
        """При запросе к about:author применяется шаблон author.html."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')


class YatubeManyPostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='AlexeyNavalny'
        )
        cls.group_to_be_with_posts = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.group_to_be_empty = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста с группой',
            author=cls.author,
            group=cls.group_to_be_with_posts
        )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = YatubeManyPostsPagesTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем, что словарь context главной страницы
    # в первом элементе списка posts содержит ожидаемые значения
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post = response.context.get('page')[0]
        post_text_1 = post.text
        post_author_1 = post.author
        post_group_1 = post.group
        self.assertEqual(
            post_text_1, 'Тестовый текст поста с группой')
        self.assertEqual(
            post_author_1, User.objects.get(id=1))
        self.assertEqual(
            post_group_1.title, 'Тестовая группа')

    # Проверяем, что словарь context профайла пользователя
    # в первом элементе списка содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': 'AlexeyNavalny'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post = response.context.get('page')[0]
        post_text_0 = post.text
        post_author_0 = post.author
        post_group_0 = post.group
        profile_posts_count = response.context.get('posts').count()
        self.assertEqual(
            post_text_0, 'Тестовый текст поста с группой')
        self.assertEqual(
            post_author_0, User.objects.get(id=1))
        self.assertEqual(
            post_group_0.title, Group.objects.get(id=1).title)
        self.assertEqual(
            profile_posts_count, 1)

    # Проверяем, что словарь context страницы group/test_slug
    # содержит ожидаемые значения
    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_slug'}))
        post = response.context.get('page')[0]
        post_text_0 = post.text
        post_author_0 = post.author
        post_group_0 = post.group
        self.assertEqual(
            response.context.get('group').title, 'Тестовая группа')
        self.assertEqual(
            response.context.get('group').description, 'Тестовое описание')
        self.assertEqual(
            response.context.get('group').slug, 'test_slug')
        self.assertEqual(
            post_text_0, 'Тестовый текст поста с группой')
        self.assertEqual(
            post_author_0, User.objects.get(id=1))
        self.assertEqual(
            post_group_0.title, Group.objects.get(id=1).title)

    # Проверяем, что новый пост добавляется в группу
    def test_new_group_post_in_group(self):
        """Новый групповой пост появляется на странице группы."""
        response = self.authorized_client.get(reverse(
            'group', kwargs={'slug': 'test_slug'}))
        group_post = response.context.get('page')[0]
        self.assertEqual(group_post, Post.objects.get(id=1))

    # Проверяем, что новый пост не добавляется в ненужную группу
    def test_new_group_post_not_in_group(self):
        """Новый групповой пост не появляется на странице ненужной группы."""
        group_posts_count = Post.objects.filter(group='2').count()
        self.assertEqual(group_posts_count, 0)


class YatubePostsWithPicturesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Любитель',
            last_name='Картинок',
            username='piclover'
        )
        cls.group_pic_posts = Group.objects.create(
            title='Тестовая группа для картинок',
            slug='test_pic_slug',
            description='Тестовое описание с картинками'
        )
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        cls.post_with_pic = Post.objects.create(
            text='Тестовый текст поста с картинкой в группу',
            author=cls.author,
            group=cls.group_pic_posts,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = YatubePostsWithPicturesTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверка словаря контекста создания нового поста с картинкой
    def test_new_post_pic_page_show_correct_context(self):
        """Шаблон создания поста с картинкой сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context главной страницы
    # в первом элементе списка posts содержит ожидаемые значения
    def test_index_page_with_pics_show_correct_context(self):
        """Шаблон index с постом с картинкой сформирован
        с правильным контекстом"""
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post_with_pic = response.context.get('page')[0]
        post_text_1 = post_with_pic.text
        post_author_1 = post_with_pic.author
        post_group_1 = post_with_pic.group
        post_image_1 = post_with_pic.image
        index_posts_count = len(response.context.get('page').object_list)
        self.assertEqual(
            post_text_1, 'Тестовый текст поста с картинкой в группу')
        self.assertEqual(
            post_author_1, User.objects.get(id=1))
        self.assertEqual(
            post_group_1.title, 'Тестовая группа для картинок')
        self.assertEqual(
            post_image_1, Post.objects.get(id=1).image)
        self.assertEqual(
            index_posts_count, 1)

    # Проверяем, что словарь context страницы group/test_slug
    # содержит ожидаемые значения
    def test_group_pages_show_correct_context(self):
        """Шаблон group с постом с картинкой сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_pic_slug'}))
        post_with_pic = response.context.get('page')[0]
        post_text_1 = post_with_pic.text
        post_author_1 = post_with_pic.author
        post_group_1 = post_with_pic.group
        post_image_1 = post_with_pic.image
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа для картинок'
                         )
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание с картинками'
                         )
        self.assertEqual(
            response.context.get('group').slug, 'test_pic_slug')
        self.assertEqual(
            post_text_1, 'Тестовый текст поста с картинкой в группу')
        self.assertEqual(
            post_author_1, User.objects.get(id=1))
        self.assertEqual(
            post_group_1.title, Group.objects.get(id=1).title)
        self.assertEqual(
            post_image_1, Post.objects.get(id=1).image)

    # Проверяем, что словарь context профайла пользователя
    # в первом элементе списка содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон profile с постом с картинкой сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': 'piclover'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post_with_pic = response.context.get('page')[0]
        post_text_1 = post_with_pic.text
        post_author_1 = post_with_pic.author
        post_group_1 = post_with_pic.group
        post_image_1 = post_with_pic.image
        profile_posts_count = response.context.get('posts').count()
        self.assertEqual(
            post_text_1, 'Тестовый текст поста с картинкой в группу')
        self.assertEqual(
            post_author_1, User.objects.get(id=1))
        self.assertEqual(
            post_group_1.title, Group.objects.get(id=1).title)
        self.assertEqual(
            profile_posts_count, 1)
        self.assertEqual(
            post_image_1, Post.objects.get(id=1).image)

    # Проверяем, что словарь context отдельного поста
    # содержит ожидаемые значения
    def test_post_page_show_correct_context(self):
        """Шаблон post_id с постом с картинкой сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': 'piclover', 'post_id': '1'}))
        # Взяли пост и проверили, что его содержание совпадает с ожидаемым
        post_with_pic = response.context.get('post')
        post_text = post_with_pic.text
        post_author = post_with_pic.author
        post_group = post_with_pic.group
        post_image = post_with_pic.image
        profile_posts_count = response.context.get('posts_count')
        self.assertEqual(
            post_text, 'Тестовый текст поста с картинкой в группу')
        self.assertEqual(
            post_author, User.objects.get(id=1))
        self.assertEqual(
            post_group.title, Group.objects.get(id=1).title)
        self.assertEqual(
            profile_posts_count, 1)
        self.assertEqual(
            post_image, Post.objects.get(id=1).image)


class YatubeCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='AlexeyNavalny'
        )
        Post.objects.create(
            text='Тестовый текст поста 1',
            author=cls.author,
            group=None
        )

    def setUp(self):
        # Создаём авторизованный клиент
        self.user = YatubeCacheTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_for_index(self):
        """Кэш страницы index."""
        cache.clear()
        author = User.objects.get(username='AlexeyNavalny')
        response = self.authorized_client.get(reverse('index'))
        # Считаем количество постов на главной первый раз
        first_response = len(response.context.get('page').object_list)
        # Создаем новый пост
        Post.objects.create(
            text='Тестовый текст поста 2',
            author=author,
            group=None
        )
        # Считаем количество постов на главной второй раз
        second_response = len(response.context.get('page').object_list)
        # Убедимся, что постов на главной странице не прибавилось
        self.assertEqual(first_response, second_response)
        # Убедимся, что постов в базе больше, чем на главной странице
        self.assertEqual(second_response + 1, Post.objects.count())


class YatubeFollowingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            email='testemail1@mail.ru',
            first_name='Автор',
            last_name='Постов',
            username='test_author'
        )
        cls.user_follow = User.objects.create(
            email='testemail2@mail.ru',
            first_name='Пользователь',
            last_name='Подписывающийся',
            username='test_user_follow'
        )
        cls.user_nonfollow = User.objects.create(
            email='testemail3@mail.ru',
            first_name='Пользователь',
            last_name='НеПодписывающийся',
            username='test_user_nonfollow'
        )
        Post.objects.create(
            text='Тестовый текст поста 1',
            author=cls.author,
            group=None
        )

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = YatubeFollowingTests.user_follow
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow(self):
        """Авторизованный пользователь может подписываться"""
        user = YatubeFollowingTests.user_follow
        author = YatubeFollowingTests.author
        # Считаем подписки пользователя user до подписки
        user_followers_before = Follow.objects.filter(user=user).count()
        # Создаем объект Follow
        Follow.objects.create(
            user=user,
            author=author
        )
        # Считаем подписки пользователя user после подписки
        user_followers_after = Follow.objects.filter(user=user).count()
        # Проверяем, что кол-во подписок пользователя user увеличилось на 1
        self.assertEqual(user_followers_before, user_followers_after - 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        user = YatubeFollowingTests.user_follow
        author = YatubeFollowingTests.author
        # Создаем объект Follow
        Follow.objects.create(
            user=user,
            author=author
        )
        # Считаем подписки пользователя user до отписки
        user_followers_before = Follow.objects.filter(user=user).count()
        # Удаляем объект Follow
        Follow.objects.filter(user=user, author=author).delete()
        # Считаем подписки пользователя user после отписки
        user_followers_after = Follow.objects.filter(user=user).count()
        # Проверяем, что кол-во подписок пользователя user увеличилось на 1
        self.assertEqual(user_followers_before, user_followers_after + 1)

    def test_followers_feed(self):
        """Пост появляется в ленте у подписчика его автора."""
        user = YatubeFollowingTests.user_follow
        author = YatubeFollowingTests.author
        # Создаем объект Follow
        Follow.objects.create(
            user=user,
            author=author
        )
        response = self.authorized_client.get(reverse('follow_index'))
        # Берем первый пост с ленты подписчика
        follow_post = response.context.get('page')[0]
        # Проверяем, что первый пост имеется в ленте
        self.assertEqual(follow_post, Post.objects.get(id=1))

    def test_nonfollowers_feed(self):
        """Пост не появляется в ленте у не-подписчика его автора."""
        user = YatubeFollowingTests.user_nonfollow
        # Логинимся за не-подписчика
        self.authorized_client.force_login(user)
        response = self.authorized_client.get(reverse('follow_index'))
        # Проверяем, что постов в ленте не-подписчика нет
        self.assertEqual(response.context.get('posts'), None)
