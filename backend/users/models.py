from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        unique=True,
        verbose_name='email',
        max_length=255,
        help_text='Email пользователя',
    )
    avatar = models.ImageField(
        upload_to='users/pictures/',
        null=True,
        blank=True,
        default=None,
        help_text='Аватар пользователя',
    )
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        blank=True,
        symmetrical=False,
        help_text='Подписки пользователя',
    )
    favourites = models.ManyToManyField(
        Recipe,
        related_name='favourited_by',
        blank=True,
        help_text='Избранные рецепты пользователя',
    )

    REQUIRED_FIELDS = [
        'username',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
