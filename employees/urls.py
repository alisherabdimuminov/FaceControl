from django.urls import path

from .views import (
    areas_view,
    add_area_view,
    delete_area_view,
    employees_view,
    add_employee_view,
    employee_view,
    edit_employee_view,
    delete_employee_view,
    departments_view,
    edit_department_view,
    add_department_view,
    employees_birth_date_view,
    attendance_view,
)


urlpatterns = [
    path("areas/", areas_view, name="areas"),
    path("areas/add/", add_area_view, name="add_area"),
    path("areas/delete/", delete_area_view, name="delete_area"),

    path("", employees_view, name="employees"),
    path("birth_dates/", employees_birth_date_view, name="employees_birth_date"),
    path("employee/<str:uuid>/", employee_view, name="employee"),
    path("employee/<str:uuid>/edit/", edit_employee_view, name="edit_employee"),
    path("employee/<str:uuid>/delete/", delete_employee_view, name="delete_employee"),
    path("add/", add_employee_view, name="add_employee"),

    path("departments/", departments_view, name="departments"),
    path("departments/add/", add_department_view, name="add_department"),
    path("departments/department/<int:pk>/edit/", edit_department_view, name="edit_department"),

    path("attendance/", attendance_view, name="attendance"),
]
