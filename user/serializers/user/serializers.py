from django.conf import settings
from rest_framework import serializers
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist

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
    username = serializers.CharField(max_length=40, required=True)
    email = serializers.CharField(max_length=40, required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ('username', 'email' 'password', 'password2')

    def validate(self, data, *args, **kwargs):
        username = data['username']
        try:
            users = User.objects.get(username=username)
            return serializers.ValidationError('Пользователь с таким именем существует.')
        except ObjectDoesNotExist:
            if data['password'] != data['password2']:
                raise serializers.ValidationError('Пароли не совпадают.')
            return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.verified = False
        user.save()

        subject = 'Подтверждение регистрации'
        message = f'Привет, {user.username}. Подтвердите свою регистрацию по ссылке: http://example.com/verify/{user.username}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        return user


class RecoveryPasswordSendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class RecoveryPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2 and len(password) < 8:
            raise serializers.ValidationError('Пароли не совпадают или меньше 8 символов.')
        return attrs


