from django.contrib import admin

from .models import (
    Coordinate,
    Area,
    AccessControl,
    Department,
    Employee,
    OutputControl,
    Vocation,
)


@admin.register(Coordinate)
class CoordinateModelAdmin(admin.ModelAdmin):
    list_display = ["latitude", "longitude", ]


@admin.register(Area)
class AreaModelAdmin(admin.ModelAdmin):
    list_display = ["name", ]


@admin.register(AccessControl)
class AccessControlModelAdmin(admin.ModelAdmin):
    list_display = ["employee", "status", "created", ]


@admin.register(Department)
class DepartmentModelAdmin(admin.ModelAdmin):
    list_display = ["name", "active", ]


@admin.register(Employee)
class EmployeeModelAdmin(admin.ModelAdmin):
    list_display = ["full_name", "department", "position", ]


@admin.register(OutputControl)
class OutputControlModelAdmin(admin.ModelAdmin):
    list_display = ["employee", "status", "created",]


@admin.register(Vocation)
class VocationModelAdmin(admin.ModelAdmin):
    list_display = ["employee", "start_date", "end_date", ]
