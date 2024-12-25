from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import History, User


@admin.register(User)
class UserModelAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ["username", "first_name", "last_name"]
    model = User
    fieldsets = (
        ("Foydalanuvchini tahrirlash", {
            "fields": ("username", "first_name", "last_name", )
        }), 
    )
    add_fieldsets = (
        ("Yangi foydalanuvchi qo'shish", {
            "fields": ("username", "password1", "password2", "first_name", "last_name", )
        }), 
    )


@admin.register(History)
class HistoryModelAdmin(admin.ModelAdmin):
    list_display = ["user", "model", "comment", "created"]
