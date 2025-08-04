from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='email',
        help_text='Введите Ваш email'
    )
    avatar = models.ImageField(
        upload_to='users/avatars',
        verbose_name='Аватар',
        help_text='Загрузите изображение',
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=35,
        verbose_name='Номер телефона',
        help_text='Введите номер телефона',
        null=True,
        blank=True
    )
    country = models.CharField(
        max_length=50,
        verbose_name='Страна',
        help_text='Введите страну проживания',
    )
    token = models.CharField(
        max_length=50,
        verbose_name='токен',
        null=True,
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ('can_block_user', 'Can block user'),
        ]

    def __str__(self):
        return self.email

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/users/default_avatar.png'