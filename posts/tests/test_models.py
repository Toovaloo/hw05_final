from django.test import TestCase
from posts.models import Post, Group, User


class PostGroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aurhor = User.objects.create(
            email='testemail@mail.ru',
            first_name='Алексей',
            last_name='Навальный'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание тестовой группы'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=cls.aurhor,
            group=cls.group
        )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = Post.objects.get(id=1)
        field_help_texts = {
            'group': 'В какой группе будет пост?',
            'text': 'Напишите пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = Post.objects.get(id=1)
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_object_name_is_text_fild_post(self):
        """Тестирование поля __str__"""
        post = Post.objects.get(id=1)
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_object_name_is_title_fild_group(self):
        """Тестирование поля __str__"""
        group = Group.objects.get(id=1)
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
