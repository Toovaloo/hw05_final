from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название", max_length=200,
                             help_text='Дайте название группе')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание",
                                   help_text='Дайте короткое описание группы')
    verbose_name = "группа"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст", help_text='Напишите пост')
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              verbose_name="Группа",
                              on_delete=models.CASCADE,
                              related_name="posts",
                              blank=True,
                              null=True,
                              help_text='В какой группе будет пост?')
    image = models.ImageField(verbose_name="Изображение",
                              upload_to='posts/',
                              blank=True, null=True,
                              help_text='Добавьте изображение')
    verbose_name = "пост"

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             verbose_name="Комментарий",
                             on_delete=models.CASCADE,
                             related_name="comments",
                             blank=True,
                             null=False,
                             help_text='К какому посту комментарий?')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name="Текст",
                            help_text='Напишите комментарий')
    created = models.DateTimeField("date published", auto_now_add=True)
    verbose_name = "коммент"

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:10]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following")
