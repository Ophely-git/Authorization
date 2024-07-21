from rest_framework import serializers

from user.models import User


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'verified', 'avatar']


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def save(self, **kwargs):
        password = self.validated_data.get('password')
        password2 = self.validated_data.get('password2')
        if password != password2 or len(password) < 8:
            raise serializers.ValidationError('Пароли не совпадает или меньше 8 символов')
        else:
            username = self.validated_data.get('username')
            email = self.validated_data.get('email')
            user = User.objects.create_user(username=username, email=email, password=password)
        return user


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


