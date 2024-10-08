from django.urls import path

from .views import *


urlpatterns = [
    path('list_all_users/', UserList.as_view()),
    path('registration/', Registration.as_view(), name='user-registration'),
    path('verify-user-email/<str:code_send>/', UserEmailVerifey.as_view(), name='user-email-verify'),
    path('change-password-send-mail/', ChangePasswordSendMail.as_view(), name='change-email-send-mail'),
    path('change-password/<str:code_send>/', ChangePassword.as_view()),
    path('change-email-send-mail/', ChangeEmailSendMail.as_view()),
    path('change-email/<str:encoded_new_email>/<str:user_id_code>/', ChangeEmail.as_view()),
    path('delete-user/', DeleteUser.as_view()),
    path('recovery-password-send-mail/', RecoveryPasswordSendMail.as_view(), name='recovery-password-send-mail'),
    path('recovery-password/<str:code_send>/', RecoveryPassword.as_view(), name='recovery-password'),
]



