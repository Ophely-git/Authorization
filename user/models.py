import random

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def upload(self, filename):
    return f'avatar/{self.username}/{filename}'


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True, blank=False)
    email = models.EmailField(unique=True, blank=False)
    verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=upload, default='no_photo.jpg', null=True, blank=True)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        user = User.objects.get(pk=self.pk)
        try:
            Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            Profile.objects.create(user=user)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    code = models.CharField(max_length=5, default=f'{random.randrange(10000, 99999)}')

    objects = models.Manager()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
