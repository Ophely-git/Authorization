from django.conf import settings
from rest_framework import serializers
from django.core.mail import send_mail

from django.core.exceptions import ObjectDoesNotExist
import re
from user.models import User


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'verified']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError('Новые пароли не совпадают.')
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError('Новый пароль не может соответствовать старому.')
        if len(data['new_password']) < 8:
            raise serializers.ValidationError('Пароль слишком короткий.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['new_password']):
            raise serializers.ValidationError('Новый пароль должен содержать хотя бы один специальный символ.')
        return data


class ChangeEmailSerializer(serializers.Serializer):
    old_email = serializers.EmailField(write_only=True, required=True)
    new_email = serializers.EmailField(write_only=True, required=True)


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=40)
    email = serializers.EmailField(max_length=40)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data, *args, **kwargs):
        password = data['password']
        password2 = data['password2']
        email = data['email']
        username = data['username']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Такой юзер уже существует.')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такой email уже зарегистрирован.')
        if len(password) < 8:
            raise serializers.ValidationError('Пароль слишком короткий.')
        if password != password2:
            raise serializers.ValidationError('Пароли не совпадают.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Пароль должен содержать хотя бы один специальный символ.')
    
        return data

    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.set_password(validated_data['password'])
        user.verified = False
        user.save()

        subject = "Подтверждение электронной почты"
        body = f"Здравствуйте{user.username}, для подтверждения вашей почты, пройдите по следующей ссылке http://localhost:8000/api/user/verified-user-email/{user.username}"
        sender = settings.EMAIL_HOST_USER
        recipients = [user.email]

        send_mail(subject, body, sender, recipients, fail_silently=False)
        return user


class VerifieSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True, required=True)
