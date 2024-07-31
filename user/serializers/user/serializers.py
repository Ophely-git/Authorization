from django.conf import settings
from rest_framework import serializers
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
import re
from user.models import User

from user.views.another.views import generate_code
class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'verified']


class RecoveryPasswordSendMailSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if not User.objects.filter(username=username, email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email и username не найден.")

        return data

    def send_password_reset_email(self):
        username = self.validated_data['username']
        email = self.validated_data['email']

        user = User.objects.get(username = username, email = email)
        user_id = user.pk

        subject = "Смена пароля"
        body = f"Здравствуйте {username}, пройдите по следующей ссылке для смены пароля http://localhost:8000/api/user/change-password/{generate_code(user_id=user_id)}"
        sender = settings.EMAIL_HOST_USER
        recipients = [email]

        send_mail(subject, body, sender, recipients, fail_silently=False)


class RecoveryPasswordSerializer(serializers.Serializer):
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


class ChangeEmailSendMailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(write_only=True, required=True)


class ChangeEmailSerializer(serializers.Serializer):
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

        user_id = user.pk
        subject = "Подтверждение электронной почты"
        body = f"Здравствуйте{user.username}, для подтверждения вашей почты, пройдите по следующей ссылке http://localhost:8000/api/user/verified-user-email/{generate_code(user_id=user_id)}"
        sender = settings.EMAIL_HOST_USER
        recipients = [user.email]

        send_mail(subject, body, sender, recipients, fail_silently=False)
        return user


class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True, required=True)


class ChangePasswordSendMailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2 and len(password) < 8:
            raise serializers.ValidationError('Пароли не совпадают или меньше 8 символов.')
        return attrs
