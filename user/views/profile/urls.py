from django.urls import path

from .views import *

urlpatterns = [
    path('list-all-profiles/', AllProfileList.as_view()),
    path('get-profile/', GetProfile.as_view()),
    path('edit-profile/', EditProfile.as_view()),
    path('delete-profile/', DeleteProfile.as_view()),
]

