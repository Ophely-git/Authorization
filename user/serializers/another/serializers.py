from rest_framework import serializers

from user.models import User


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(max_length=255, write_only=True)
