from django.urls import path

from .views import *

urlpatterns = [
    path('list_all_users/', UserList.as_view()),
    path('registration/', Registration.as_view()),
    path('change-password-step-one/', ChangePasswordStepOne.as_view()),
    path('change-password/<str:user_id>/', ChangePassword.as_view()),
    path('change-email/', ChangeEmail.as_view()),
    path('delete-user/', DeleteUser.as_view()),
    path('recovery-password-send-mail/', RecoveryPasswordSendMail.as_view()),
    path('recovery-password/<str:code_send>/', RecoveryPassword.as_view()),
    path('test/<str:username>/', Test.as_view()),
]
