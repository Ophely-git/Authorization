from rest_framework import generics
from rest_framework.authentication import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
import jwt
from django.conf import settings
import random
import string

from itsdangerous import URLSafeTimedSerializer
from user.models import User
from user.serializers.another.serializers import *


def generate_email_token(new_email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps({"new_email": new_email})

def decode_email_token(token):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token, max_age=3600)
        return data
    except Exception as e:
        return None


def decode_token(request):
    token = str(request.headers.get('Authorization')).split(' ')[1]
    decode = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')
    return decode['user_id']


def generate_code(user_id):
    lenght = 24


    characters = string.ascii_letters + string.digits

    code = ''.join(random.choice(characters) for i in range(lenght))
    code_with_id = code[:8] + str(user_id) + code[8:]

    return code_with_id


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Неверный логин.'}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        refresh.payload.update({
            'user_id': user.id,
        })
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class LogoutAPI(generics.GenericAPIView):
    serializer_class = RefreshSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        refresh = request.data.get('refresh')
        token = RefreshToken(refresh)
        token.blacklist()
        return Response({'detail': 'Выход успешен'}, status=status.HTTP_200_OK)


class RefreshAccessTokenAPI(generics.GenericAPIView):
    serializer_class = RefreshSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        token = request.data.get('refresh')
        token = str(RefreshToken(token).access_token)
        return Response({'access': token}, status=status.HTTP_200_OK)

