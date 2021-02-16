from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class CustomUser(UserAdmin):
    readonly_fields = ("id",)
    list_display = ("id", "email", "first_name", "last_name")


admin.site.unregister(User)
admin.site.register(User, CustomUser)
