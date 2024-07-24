from django.test import TestCase
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from .models import *


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            username='test',
            email='test@test.com',
        )
        user.set_password('qwe159753')
        user.save()

    def test_username(self):
        print(f'start test username')
        user = User.objects.get(pk=1)
        username = user.get_username()
        print(f'username: {username}. Необходимо: test')
        self.assertEqual(username, 'test')

    def test_email(self):
        print(f'start test email')
        user = User.objects.get(pk=1)
        email = user.email
        print(f'email: {email}. Необходимо: test@test.com')
        self.assertEqual(email, 'test@test.com')

    def test_password(self):
        print(f'start test password')
        user = User.objects.get(pk=1)
        print(f"check_password: {user.check_password('qwe159753')}. "
              f"Необходимо True")
        self.assertEqual(user.check_password('qwe159753'), True)


class ProfileModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            username='test',
            email='test@test.com',
        )
        user.set_password('qwe159753')
        user.save()

    def test_check_profile(self):
        print(f'start test check profile')
        user = User.objects.get(pk=1)
        profile = user.profile
        self.assertEqual(profile, 'test')

