from django.conf import settings
from rest_framework import serializers
from django.core.mail import send_mail

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
            raise serializers.ValidationError('Неверно введен новый пароль.')
        return data


class ChangeEmailSerializer(serializers.Serializer):
    old_email = serializers.EmailField(write_only=True, required=True)
    new_email = serializers.EmailField(write_only=True, required=True)


class DeleteUserSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class RegistrationSerializer(serializers.Serializer):
    password = serializers.CharField( write_only=True)
    password2 = serializers.CharField( write_only=True)
    username = serializers.CharField(max_length=40)
    email = serializers.CharField(max_length=40)

    class Meta:
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, data, *args, **kwargs):
        users = User.objects.get(username=username)
        username = data['username']
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Пароли не совпадают.')
        if username == users:
            raise serializers.ValidationError('Такой пользователь уже существует.')
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password2']
        )
        user.verified = False
        user.save()

        subject = 'Подтверждение регистрации'
        message = f'Привет, {user.username}. Подтвердите свою регистрацию по ссылке: http://example.com/verify/{user.username}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        return user