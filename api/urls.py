from django.urls import path, include

from .views import check_location, check_passport, faceid


urlpatterns = [
    path("auth/", include("users.urls")),
    path("employees/", include("employees.urls")),

    path("location/", check_location, name="check_location"),
    path("passport/", check_passport, name="check_passport"),
    path("faceid/", faceid, name="faceid"),
]
