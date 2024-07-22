from rest_framework import serializers

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
