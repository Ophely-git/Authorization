from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.utils import extend_schema
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import string
import random
from django.contrib.auth.models import AbstractUser
from django.db import models

from user.serializers.user.serializers import *
from user.views.another.views import decode_token, generate_email_token, decode_email_token


class UserList(generics.GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        description='Список всех пользователей. Только для админа!'
    )
    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response({'detail': serializer.data}, status=status.HTTP_200_OK)


class Registration(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            username = serializer.validated_data['username']
            return Response({
                'detail': f'Пользователь {username} успешно зарегестринован.'
            }, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEmailVerifey(generics.GenericAPIView):
    serializer_class = VerifySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user_id_code = kwargs.get('code_send')
        user_id = user_id_code[8:-16]
        user = User.objects.get(pk=user_id)
        username = user.username
        user.verified = True
        user.save()

        return Response({"detail": f"Пользователь {username} успешно подтвердил email."},
                        status=status.HTTP_200_OK)


class RecoveryPasswordSendMail(generics.GenericAPIView):
    serializer_class = RecoveryPasswordSendMailSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        # parameters=[RecoveryPasswordSendEmailSerializer],
        description='Если email и Username есть в базе и совпадают, отправляется сообщение с ссылкой'
                    ' на другой URL адрес. Доступно для всех пользователей.'
    )
    def post(self, request):
        serializer = RecoveryPasswordSendMailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_password_reset_email()
            return Response({"message": "Ссылка для смены пароля отправлена на ваш email."},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecoveryPassword(generics.GenericAPIView):
    serializer_class = RecoveryPasswordSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        # parameters=[RecoveryPasswordSendEmailSerializer],
        description='При переходе на эту ссылку API получает секретный код.'
                    ' Пользователь перешедший по этой ссылке открывает страницу'
                    ' на востановления пароля.'
    )

    def post(self, request, *args, **kwargs):
        user_code = kwargs.get('code_send')
        user_id = user_code[8:-16]
        user = User.objects.get(pk=user_id)
        old_password = request.data.get('old_password')
        if user.check_password(old_password):
            serializer = RecoveryPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()

            subject = "Уведомление о смене пароля"
            body = (f"Здравствуйте {user.username}, ваш пароль был изменён. В случаи если это были не вы, свяжитесь с администрацией."
                    f" \nС уважением Администрация сайта КрутойСайтОтДимыИБажена.ру")
            sender = settings.EMAIL_HOST_USER
            recipients = [user.email]
            send_mail(subject, body, sender, recipients, fail_silently=False)

            return Response({
                'detail': f'Пользователь {user.username} сменил пароль.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Старый пароль не подходит.'},
                            status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailSendMail(generics.GenericAPIView):
    serializer_class = ChangeEmailSendMailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description=f'Вводится новый адрес электронной почты.'
                    f'На новый электронный и старый адрес отправляется письмо. '
                    f'На новый с ссылкой на страницу изменения почты. '
                    f'На старый сообщении о смене электронной почты.'
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        new_email = request.data.get('new_email')
        current_email = user.email
        if not new_email:
            return Response({"error": "Новый электронный адрес не был указан"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            user.unconfirmed_new_email = new_email
            encoded_new_email = generate_email_token(new_email)
            user_id_code = generate_code(user.pk)

            #Send message to current user email address.
            subject = "Уведомление о смене email"
            url = f"http://127.0.0.1:8000/api/user/change-email/{encoded_new_email}/{user_id_code}"
            message = (f"Здравствуйте {user.username}, вы хотите изменить вашу электронную почту."
                    f" В случаи если это были не вы, свяжитесь с командой BigCookingIsland. ")
            sender = settings.EMAIL_HOST_USER
            recipients = [current_email]
            send_mail(subject, message, sender, recipients)

            #Send message to new user email address.
            subject = "Уведомление о смене email"
            html_message = render_to_string('user/email_change.html', {'username': user.username, 'url': url})
            plain_message = strip_tags(html_message)
            sender = settings.EMAIL_HOST_USER
            recipients = [new_email]
            send_mail(subject, plain_message, sender, recipients, html_message=html_message)

            return Response(f'Пользователь {user.username} хочет поменять электронную почту.'
                            f' URL на подтверждение смены посты был отправлен на новый адрес.', status=status.HTTP_200_OK)


class ChangeEmail(generics.GenericAPIView):
    serializer_class = ChangeEmailSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description='Функция обрабатывает ссылку с кодированным новым имейлом и пользователем.'
                    ' Если данные проходят проверки происходит смена электронного адреса пользователя.'
    )
    def get(self, request, *args, **kwargs):
        try:
            user_id_code = kwargs.get('user_id_code')
            user_id = user_id_code[8:-16]
        except (ValueError, TypeError):
            return Response({"error": "Не корректный код пользователя."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
            print(user.unconfirmed_new_email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        try:
            new_email = kwargs.get('encoded_new_email')
            decode_code = decode_email_token(new_email)
            new_email = decode_code['new_email']
        except (ValueError, TypeError):
            return Response({"error": "Не корректный код смены email."}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.save()
        return Response({
            'detail': f'{user.username} ваш email изменен на {new_email}.'
        }, status=status.HTTP_200_OK)


class DeleteUser(generics.GenericAPIView):
    serializer_class = DeleteUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description='Удаление пользователя. '
                    'Для удаления необходимо заполнить правильный текущий пароль.'
                    ' Только для авторизованных пользователей.'
    )
    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        enter_user_password = request.data.get('password')
        if user.check_password(enter_user_password):
            user.delete()
            return Response({'detail': 'Пользователь был успешно удален.'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Неверно введен пароль.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordSendMail(generics.GenericAPIView):
    serializer_class = ChangePasswordSendMailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        # parameters=[RecoveryPasswordSendEmailSerializer],
        description='Если email и пароль совпадают, отправляется сообщение с ссылкой'
                    ' на другой URL адрес. Только для авторизованных пользователей.'
    )
    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        email = request.data.get('email')
        password = request.data.get('password')
        if user.check_password(password) and user.email == email:
            subject = user.username
            secret_code = ''.join([random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase) for i in range(10)])
            code_send = secret_code + f'{user.pk}' + secret_code
            message = (f'{subject}, для восстановления пароля перейдите по ссылке'
                       f'http://127.0.0.1:8000/api/user/recovery-password/{code_send}')
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return Response({
                'detail': f'Письмо {user.username} отправлено на почту {email}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Неверно введен пароль или email.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description='При переходе на эту ссылку API получает секретный код.'
                    ' Пользователь перешедший по этой ссылке открывает страницу'
                    ' создания нового пароля.'
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_pk = kwargs['code_send'][10:-10]
        try:
            user = User.objects.get(pk=user_pk)
            user.set_password(serializer.validated_data['password'])
            return Response({
                'detail': f'Пользователь {user.username} поменял пароль'
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({
                'detail': 'Такого пользователя не существует.'
            }, status=status.HTTP_404_NOT_FOUND)
