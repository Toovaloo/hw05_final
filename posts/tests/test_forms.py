import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User
from django.core.files.uploadedfile import SimpleUploadedFile


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # Создаем запись в базе данных
        cls.author = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный',
            username='AlekseyNavalny'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание тестовой группы'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаём неавторизованный клиент
        self.guest_client = Client()
        # Создаём авторизованный клиент
        self.user = PostFormTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост"""
        # Подсчитаем количество постов
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст 2',
            'group': 1,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/')
        # Проверяем, что создался пост
        self.assertTrue(Post.objects.filter(text='Тестовый текст 2').exists())
        # Проверяем, что количество постов увеличилось
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует и сохраняет пост"""
        # Подготавливаю новые данные
        form_data_new = {
            'text': 'Новый текст поста',
            'group': 1,
        }
        # Заполняю форму post_edit по адресу существующего поста новыми данными
        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': self.user.username, 'post_id': '1'}),
            data=form_data_new,
            follow=True)
        # Обновляю взятый ранее пост
        # Проверяем, что отредактировался пост
        self.assertTrue(Post.objects.filter(text='Новый текст поста').exists())
        # Проверяем, что поста со старыми данными уже нет
        self.assertFalse(Post.objects.filter(text='Тестовый текст').exists())
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': '1'}))


class PostFormWithPicturesTests(TestCase):
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
        cls.post_with_pic = Post.objects.create(
            text='Тестовый текст поста с картинкой в группу',
            author=cls.author,
            group=cls.group_pic_posts
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
        self.user = PostFormWithPicturesTests.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост с картинкой"""
        # Подсчитаем количество постов
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
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
        form_data = {
            'text': 'Тестовый текст 2',
            'group': 1,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/')
        # Проверяем, что создался пост
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст поста с картинкой в группу').exists())
        # Проверяем, что количество постов увеличилось
        self.assertEqual(Post.objects.count(), posts_count + 1)
