from django.contrib import admin

from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'verified']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']

