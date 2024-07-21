from django.urls import path

from .views import *

urlpatterns = [
    path('list_all_users/', UserList.as_view()),
    path('registration/', Registration.as_view()),
    path('change-password/', ChangePassword.as_view()),
]
