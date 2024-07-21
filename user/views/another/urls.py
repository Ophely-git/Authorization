from django.urls import path

from .views import *

urlpatterns = [
    path('login/', LoginAPI.as_view()),
    path('logout/', LogoutAPI.as_view()),
    path('refresh-access-token/', RefreshAccessTokenAPI.as_view()),
]
