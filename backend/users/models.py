from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    '''Модель пользователя.'''
    username = models.CharField(
        max_length=150, unique=True,
        verbose_name='Никнейм',
    )
    email = models.EmailField(
        max_length=254, unique=True,
        verbose_name='Адрес электронной почты пользователя',
    )
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя пользователя')
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия пользователя')
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Подписан ли текущий пользователь на этого',
    )
    password = models.CharField(max_length=150,
                                verbose_name='Пароль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель для подписок.'''
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('author_id',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
