from unittest.mock import patch
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.models import *
from user.serializers.user.serializers import RecoveryPasswordSerializer
from user.views.another.views import generate_code


# test command - python3.12 manage.py test user.tests.test_bazhen_views
class UserRegistrationTest(APITestCase):
    def test_registration(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword!',
            'password2': 'newpassword!',
            'email': 'newuser@example.com'
        }

        url = reverse('user-registration')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class UserEmailVerifyTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')
        self.user.verified = False
        self.user.save()
        self.code_send = generate_code(str(self.user.id))

    def test_email_verification(self):
        url = reverse('user-email-verify', kwargs={'code_send': self.code_send})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Получаем последнее состояние бд
        self.assertTrue(self.user.verified)

        expected_message = f"Пользователь {self.user.username} успешно подтвердил email."
        self.assertEqual(response.data['detail'], expected_message)


class RecoveryPasswordSendMailTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com')
        self.user.save()
        self.url = reverse('recovery-password-send-mail')

    def test_recovery_password_success(self):
        """
        Тест успешной отправки письма на восстановление пароля, если email и username совпадают.
        """
        data = {
            'username': 'testuser',
            'email': 'test@gmail.com'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Ссылка для смены пароля отправлена на ваш email.")


class RecoveryPasswordTest(APITestCase):
    def setUp(self):
        self.data = {
            'old_password': 'Oldpassword123!',
            'new_password': 'Test111!',
            'new_password2': 'Test111!'
        }

    def test_successful_validation(self):
        """Тест успешной валидации пароля."""
        serializer = RecoveryPasswordSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch(self):
        """Тест на несовпадение нового пароля и его подтверждения."""
        data = self.data.copy()
        data['new_password2'] = 'differentpassword!'
        serializer = RecoveryPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Новые пароли не совпадают.', serializer.errors['non_field_errors'])

    def test_old_and_new_password_same(self):
        """Тест на совпадение старого и нового пароля."""
        data = self.data.copy()
        data['new_password'] = 'Oldpassword123!'
        data['new_password2'] = 'Oldpassword123!'
        serializer = RecoveryPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Новый пароль не может соответствовать старому.', serializer.errors['non_field_errors'])

    def test_password_too_short(self):
        """Тест на слишком короткий новый пароль."""
        data = self.data.copy()
        data['new_password'] = 'short!'
        data['new_password2'] = 'short!'
        serializer = RecoveryPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Пароль слишком короткий.', serializer.errors['non_field_errors'])

    def test_password_no_special_character(self):
        """Тест на отсутствие специального символа в новом пароле."""
        data = self.data.copy()
        data['new_password'] = 'newpassword456'
        data['new_password2'] = 'newpassword456'
        serializer = RecoveryPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Новый пароль должен содержать хотя бы один специальный символ.',
                      serializer.errors['non_field_errors'])


