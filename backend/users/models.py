from django.db import models
from django.contrib.auth.models import AbstractUser

from recipes.models import Recipe


class User(AbstractUser):
    avatar = models.ImageField(upload_to='users/pictures/', null=True,
                               blank=True,
                               default='users/pictures/default.png',
                               help_text='Аватар пользователя')
    following = models.ManyToManyField("self", related_name='followers',
                                       blank=True,
                                       symmetrical=False,
                                       help_text='Подписки пользователя')
    favourites = models.ManyToManyField(Recipe,
                                        related_name='user_favourites',
                                        blank=True,
                                        help_text='Избранные рецепты '
                                                  'пользователя')
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'




