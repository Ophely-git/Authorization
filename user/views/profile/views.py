from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from user.views.another.views import decode_token
from user.models import Profile
from user.serializers.profile.serializers import *


class AllProfileList(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        description='Список всех профилей. Только для админа.'
    )
    def get(self, request, *args, **kwargs):
        profiles = Profile.objects.all()
        serializer = AllProfilesListSerializer(profiles, many=True)

        return Response({
            'users': serializer.data,
        }, status=status.HTTP_200_OK)


class GetProfile(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description='Получить конкретный профиль. Только для авторизованных пользователей.',
    )
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        profile = user.profile
        serializer = AllProfilesListSerializer(profile, many=False)
        return Response({
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class EditProfile(generics.GenericAPIView):
    serializer_class = EditProfileSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description='Редактирование профиля. Только для авторизованных пользователей.'
                    ' Возможно сменить поля Имя, Фамилия, Возраст, Аватар.'
    )
    def patch(self, request, *args, **kwargs):
        user = User.objects.get(pk=decode_token(request))
        profile = user.profile
        profile.first_name = request.data.get('first_name', profile.first_name)
        profile.last_name = request.data.get('last_name', profile.last_name)
        profile.age = request.data.get('age', profile.age)
        profile.avatar = request.data.get('avatar', profile.avatar)
        profile.save()
        serializer = EditProfileSerializer(profile)
        return Response({
            'profile': serializer.data
        }, status=status.HTTP_200_OK)


class DeleteProfile(generics.GenericAPIView):
    serializer_class = DeleteProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description='Удаление профиля. Только для авторизованных пользователей.'
    )
    def delete(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=decode_token(request))
        username = profile.user.username
        profile.user.delete()
        return Response({
            'detail': f'Профиль {username} был удален.'
        }, status=status.HTTP_200_OK)
