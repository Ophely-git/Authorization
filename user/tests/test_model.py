from django.test import TestCase

from user.models import *


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
        user = User.objects.get(pk=1)
        username = user.get_username()
        print(f'username: {username}. Необходимо: test')
        self.assertEqual(username, 'test')

    def test_email(self):
        user = User.objects.get(pk=1)
        email = user.email
        print(f'email: {email}. Необходимо: test@test.com')
        self.assertEqual(email, 'test@test.com')

    def test_password(self):
        user = User.objects.get(pk=1)
        print(f"check_password: {user.check_password('qwe159753')}. "
              f"Необходимо True")
        self.assertEqual(user.check_password('qwe159753'), True)

    def test_verified(self):
        user = User.objects.get(pk=1)
        print(f"verified: {user.verified}. Необходимо False")
        self.assertEqual(user.verified, False)


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
        user = User.objects.get(pk=1)
        profile = user.profile
        self.assertEqual(profile.user.username, 'test')

    def test_first_name(self):
        user = User.objects.get(pk=1)
        profile = user.profile
        print(f'first_name: {profile.first_name}. Необходимо ""')
        self.assertEqual(profile.first_name, '')

    def test_last_name(self):
        user = User.objects.get(pk=1)
        profile = user.profile
        print(f'last_name: {profile.last_name}. Необходимо ""')
        self.assertEqual(profile.last_name, '')

    def test_age(self):
        user = User.objects.get(pk=1)
        profile = user.profile
        print(f'age: {profile.age}. Необходимо ""')
        self.assertEqual(profile.age, None)

    def test_avatar(self):
        user = User.objects.get(pk=1)
        profile = user.profile
        print(f'avatar: {profile.avatar.url}. Необходимо "/media/no_photo.jpg"')
        self.assertEqual(profile.avatar.url, '/media/no_photo.jpg')


