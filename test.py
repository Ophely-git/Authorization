def get(self, request, *args, **kwargs):
    user_id_code = kwargs.get('user_id')
    user_id = user_id_code[8:-16]
    user = User.objects.get(pk=user_id)
    username = user.username
    user.verified = True
    user.save()

    return Response({"detail": f"Пользователь {username} успешно подтвердил email."},
                    status=status.HTTP_200_OK)
