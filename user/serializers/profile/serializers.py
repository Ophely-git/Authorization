from rest_framework import serializers

from user.models import Profile
from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'verified']


class AllProfilesListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'first_name', 'last_name', 'age', 'data_joined', 'avatar']


class EditProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'first_name', 'last_name', 'age', 'avatar']


class DeleteProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    age = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'first_name', 'last_name', 'age', 'avatar']





