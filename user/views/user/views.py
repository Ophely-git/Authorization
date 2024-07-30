from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.core.mail import send_mail
import string
import random

from user.models import User
from user.serializers.user.serializers import *
from user.views.another.views import decode_token


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


class Verifei(generics.GenericAPIView):
    serializer_class = VerifySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):

        user_id_code = kwargs.get('user_id')
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
        user_code = kwargs.get('user_id')
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


class ChangeEmail(generics.GenericAPIView):
    serializer_class = ChangeEmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        now_user = User.objects.get(pk=decode_token(request))
        old_email = request.data.get('old_email')
        new_email = request.data.get('new_email')
        change_email_user = User.objects.get(email=old_email)
        if now_user == change_email_user:
            change_email_user.email = new_email
            change_email_user.save()
            serializer = UserListSerializer(change_email_user)
            return Response({
                'detail': f'Ваш email изменен.',
                'user': serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Некорректно введен старый email.'},
                            status=status.HTTP_400_BAD_REQUEST)


# TODO: Доделать
class SendVerificationMail(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        return Response({'detail': 'ok'})


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


class Test(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        username = kwargs
        print(username)
        return Response({'detail': 'ok'})