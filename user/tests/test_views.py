import json

from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.models import *


class UserAPITest(APITestCase):

    login_url = '/api/user/login/'
    logout_url = '/api/user/logout/'

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='admin', email='admin@admin.com')
        user.set_password('admin')
        user.verified = True
        user.save()

    def test_login(self):
        user = User.objects.get(pk=1)
        data = {
            'username': user.username,
            'password': 'admin'
        }

        # Тест логин по username
        response = self.client.post(self.login_url, data=data)
        access_token = response.data['access']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', json.loads(response.content))

        # Тест логин по email
        data['username'] = user.email

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        user = User.objects.get(pk=1)
        data = {
            'username': user.email,
            'password': 'admin'
        }

        response = self.client.post(self.login_url, data=data)
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Q ' + access_token)

        response = client.post(self.logoёut_url, {'refresh': refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['detail'], 'Выход успешен')
