from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ObjectDoesNotExist, ValidationError

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






class ChangePassword(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        old_password = request.data.get('old_password')
        if user.check_password(old_password):
            serializer = ChangePasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_password = request.data.get('new_password')
            user.set_password(new_password)
            user.save()
            return Response({
                'detail': f'Пользователь {user.username} сменил пароль.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Старый пароль не подходит.'}, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({'detail': 'Некорректно введен старый email.'}, status=status.HTTP_400_BAD_REQUEST)


# TODO: Доделать
class SendVerificationMail(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        return Response({'detail': 'ok'})


class DeleteUser(generics.GenericAPIView):
    serializer_class = DeleteUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        enter_user_password = request.data.get('password')
        if user.check_password(enter_user_password):
            user.delete()
            return Response({'detail': 'Пользователь был успешно удален'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Невверно введен пароль'}, status=status.HTTP_400_BAD_REQUEST)


class Registration(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
    #TODO почистить код, трай эксепт для проверки юзернэйма и имейла
        serializer=RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            username = serializer.validated_data['username']
            return Response({
                'detail': f'Пользователь {username} успешно зарегестринован.'
            }, status=status.HTTP_201_CREATED )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #TODO не ясно как обработать ошибку когда пользователь с таким username уже существует.




class Verifei(generics.GenericAPIView):
    serializer_class = VerifieSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):

        username = kwargs.get('username')
        user = User.objects.get(username=username)
        user.verified = True
        user.save()

        return Response({"detail": f"Пользователь {username} успешно подтвердил email."}, status=status.HTTP_200_OK)







# # views.py
# from django.shortcuts import redirect
# from google_auth_oauthlib.flow import Flow
# import os
#
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # для разработки, отключает проверку HTTPS
#
# CLIENT_SECRETS_FILE = 'C:/Users/Bazhe/Desktop/DRF Rest/client_secret_821344542102-6coc7ajdp4h9ptigjesi0fme9sfpb90a.apps.googleusercontent.com.json'
# SCOPES = ['https://www.googleapis.com/auth/gmail.send']
# REDIRECT_URI = 'http://localhost:8000/oauth2callback'
#
# def authorize(request):
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true'
#     )
#     request.session['state'] = state
#     return redirect(authorization_url)
#
#
#
# # views.py
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from django.conf import settings
#
# def oauth2callback(request):
#     state = request.session['state']
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         state=state,
#         redirect_uri=REDIRECT_URI
#     )
#     flow.fetch_token(authorization_response=request.build_absolute_uri())
#
#     credentials = flow.credentials
#     request.session['credentials'] = credentials_to_dict(credentials)
#
#     return redirect('send_test_email')
#
# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }
#
#
# # views.py
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
#
# def send_test_email(request):
#     if 'credentials' not in request.session:
#         return redirect('authorize')
#
#     credentials = Credentials(**request.session['credentials'])
#     service = build('gmail', 'v1', credentials=credentials)
#
#     message = {
#         'raw': base64.urlsafe_b64encode(
#             f'To: recipient@example.com\n'
#             f'Subject: Test Email\n\n'
#             f'This is a test email sent using OAuth2.'
#         ).decode()
#     }
#
#     service.users().messages().send(userId='me', body=message).execute()
#     return HttpResponse('Email sent successfully!')
