from django.urls import path

from .views import (
    change_password,
    histories,
    login,
    profile,
    toggle_user_active,
    users,
)


urlpatterns = [
    path("login/", login, name="login"),
    path("profile/", profile, name="profile"),
    path("users/", users, name="users"),
    path("toggle/", toggle_user_active, name="toggle"),
    path("change_pwd/", change_password, name="change_password"),
    path("histories/", histories, name="histories"),
]
