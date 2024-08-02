import random

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def upload(self, filename):
    return f'avatar/{self.username}/{filename}'


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, blank=False, verbose_name="Имя пользователя")
    email = models.EmailField(unique=True, blank=False, verbose_name="Email")
    verified = models.BooleanField(default=False, verbose_name="Подтверждён")
    unconfirmed_new_email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ["username", "verified"]
        indexes = [
            models.Index(fields=["username", "verified"])
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
        
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        user = User.objects.get(pk=self.pk)
        try:
            Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            Profile.objects.create(user=user)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь", blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True)
    age = models.IntegerField(verbose_name="Возраст", blank=True, null=True)
    data_joined = models.DateTimeField(auto_now_add=True, verbose_name="Присоединился", blank=True)
    avatar = models.ImageField(upload_to=upload, default='no_photo.jpg', null=True, blank=True, verbose_name="Аватар")

    objects = models.Manager()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
