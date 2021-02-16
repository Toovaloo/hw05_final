from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, User, Post
from django.core.cache import cache


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class YatubeURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса group/<slug>/
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='navalny'
        )
        User.objects.create(
            email='kreed@mail.ru',
            first_name='Егор',
            last_name='Крид',
            username='kreed'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            description='Тестовое описание группы',
            slug='test-slug',
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = YatubeURLTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_home_url_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_location(self):
        """Страница /group/test-slug/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_location(self):
        """Страница профиля доступна любому пользователю."""
        response = self.guest_client.get('/navalny/')
        self.assertEqual(response.status_code, 200)

    def test_post_location(self):
        """Страница поста доступна любому пользователю."""
        response = self.guest_client.get('/navalny/1/')
        self.assertEqual(response.status_code, 200)

    # Проверяем страницы, доступные только авторизованным пользователям
    def test_new_post_authorized_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_author_location(self):
        """Страница /edit/ доступна авторизованному автору."""
        response = self.authorized_client.get('/navalny/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_anonimous_location(self):
        """Страница /new/ не доступна анонимному пользователю."""
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_edit_post_anonimous_location(self):
        """Страница /edit/ не доступна анонимному пользователю."""
        response = self.guest_client.get('/navalny/1/edit/')
        self.assertEqual(response.status_code, 302)

    # Проверяем редирект для неавторизованного пользователя
    def test_new_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    # Проверяем редирект для авторизованного пользователя не автора
    def test_edit_url_redirect_authorized_no_author_on_post(self):
        """Страница /edit/ перенаправит авторизованного не автора
        на страницу поста."""
        self.user = User.objects.get(username='kreed')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get('/navalny/1/edit/')
        self.assertRedirects(
            response, '/navalny/1/')

    # Шаблоны по адресам
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new_post.html': '/new/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_uses_correct_template(self):
        """Страница /edit/ использует шаблон new_post.html"""
        response = self.authorized_client.get('/navalny/1/edit/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_about_author_page_accessible_by_name(self):
        """URL static_pages about:author доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page_accessible_by_name(self):
        """URL static_pages about:tech доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_404_error(self):
        """Для несуществующих страниц возвращается ошибка 404."""
        response = self.guest_client.get(reverse('error_404'))
        self.assertEqual(response.status_code, 404)


class YatubeURLCommentsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='navalny'
        )
        cls.user = User.objects.create(
            email='kreed@mail.ru',
            first_name='Миша',
            last_name='Маваши',
            username='misha'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=None
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = YatubeURLCommentsTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_cannot_comment(self):
        """При попытке добавить коммент неавторизованного юзера
        редиректнет в авторизацию."""
        response = self.guest_client.get('/navalny/1/comment')
        self.assertRedirects(
            response, '/auth/login/?next=/navalny/1/comment')

    def test_authorized_can_comment(self):
        """При попытке добавить коммент авторизованного юзера
        редиректнет на страницу с постом и формой."""
        response = self.authorized_client.get('/navalny/1/comment')
        self.assertRedirects(
            response, '/navalny/1/')
