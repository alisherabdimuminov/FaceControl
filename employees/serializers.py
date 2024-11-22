from datetime import timedelta
from zoneinfo import ZoneInfo
from rest_framework import serializers

from .models import (
    Coordinate, 
    Area,
    Employee,
    Department,
    AccessControl,
    OutputControl,
)


class DepartmentModelSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField("count_employees")
    def count_employees(self, obj):
        return Employee.objects.filter(department=obj.pk, active=True).count()
    class Meta:
        model = Department
        fields = ("id", "name", "active", "employees", )

    
class EmployeeModelSerializer(serializers.ModelSerializer):
    department = DepartmentModelSerializer(Department, many=False)
    class Meta:
        model = Employee
        fields = ("uuid", "handle", "full_name", "department", "position", "gender", "working_time", "birth_date", "image", "country", "city", "town", "address", "phone", )


class CreateEmployeeModelSerializer(serializers.ModelSerializer):
    # birth_date = serializers.DateField(format="%d-%m-%Y")
    class Meta:
        model = Employee
        fields = ("uuid", "handle", "full_name", "department", "position", "gender", "working_time", "birth_date", "image", "country", "city", "town", "address", "phone", )


class CoordinateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = ("latitude", "longitude", )

    
class AreaModelSerializer(serializers.ModelSerializer):
    coordinates = CoordinateModelSerializer(Coordinate, many=True)

    class Meta:
        model = Area
        fields = ("id", "name", "coordinates", )


class AttendancesModelSerializer(serializers.ModelSerializer):
    requires_context = True
    attendance_access = serializers.SerializerMethodField("attendance_access_func")
    attendance_access_time = serializers.SerializerMethodField("attendance_access_time_func")
    attendance_access_area = serializers.SerializerMethodField("attendance_access_area_func")
    attendance_output = serializers.SerializerMethodField("attendance_output_func")
    attendance_output_time = serializers.SerializerMethodField("attendance_output_time_func")

    def attendance_access_func(self, obj):
        request = self.context.get("request")
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        access_control = AccessControl.objects.filter(employee_id=obj.pk, created__day=day, created__month=month, created__year=year)
        if access_control:
            access_control = access_control.last()
            return access_control.status
        return "did_not_come"

    def attendance_access_time_func(self, obj):
        request = self.context.get("request")
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        access_control = AccessControl.objects.filter(employee=obj, created__day=day, created__month=month, created__year=year)
        if access_control:
            access_control = access_control.last()
            return access_control.created.astimezone(ZoneInfo("Asia/Tashkent")).strftime("%H:%M")
        return "-:-"
    
    def attendance_access_area_func(self, obj):
        request = self.context.get("request")
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        access_control = AccessControl.objects.filter(employee=obj, created__day=day, created__month=month, created__year=year)
        if access_control:
            access_control = access_control.last()
            return access_control.area.name
        return "Noma'lum"
    
    def attendance_output_func(self, obj):
        request = self.context.get("request")
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        output_control = OutputControl.objects.filter(employee=obj, created__day=day, created__month=month, created__year=year)
        if output_control:
            output_control = output_control.last()
            return output_control.status
        return "at_work"
    
    def attendance_output_time_func(self, obj):
        request = self.context.get("request")
        day = request.GET.get("day")
        month = request.GET.get("month")
        year = request.GET.get("year")
        output_control = OutputControl.objects.filter(employee=obj, created__day=day, created__month=month, created__year=year)
        if output_control:
            output_control = output_control.last()
            return output_control.created.astimezone(ZoneInfo("Asia/Tashkent")).strftime("%H:%M")
        return "-:-"

    class Meta:
        model = Employee
        fields = (
            "uuid", "full_name",
            "attendance_access", "attendance_access_time",
            "attendance_access_area", "attendance_output",
            "attendance_output_time",
        )
