from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        unique=True,
        verbose_name='email',
        max_length=255,
    )
    avatar = models.ImageField(
        upload_to='users/pictures/',
        default='',
        help_text='Аватар пользователя',
    )

    REQUIRED_FIELDS = [
        'username',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('follower', 'following')

    def __str__(self):
        return self.following

    def clean(self):
        super().clean()

        if self.follower == self.following:
            raise ValidationError(
                {
                    'follower': 'Cannot follow yourself',
                }
            )
