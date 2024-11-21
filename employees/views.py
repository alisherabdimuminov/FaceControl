import base64
from datetime import datetime, timedelta

from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import decorators
from rest_framework import permissions
from django.core.files.base import ContentFile

from users.models import History
from .models import (
    Coordinate,
    Area,
    Employee,
    Department,
)
from .serializers import (
    CoordinateModelSerializer,
    AreaModelSerializer,
    EmployeeModelSerializer,
    DepartmentModelSerializer,
    CreateEmployeeModelSerializer,
    AttendancesModelSerializer,
)


# Employee
@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def employees_view(request: HttpRequest):
    department_pk = request.GET.get("department") or 0
    if department_pk == 0 or department_pk == "0":
        employees_obj = Employee.objects.filter(active=True)
        employees = EmployeeModelSerializer(employees_obj, many=True)
        print(employees_obj)
    else:
        department = Department.objects.get(pk=department_pk)
        employees_obj = Employee.objects.filter(active=True, department=department)
        employees = EmployeeModelSerializer(employees_obj, many=True)
        print(employees_obj)
    return Response({
        "status": "success",
        "code": "200",
        "data": employees.data,
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def employees_birth_date_view(request: HttpRequest):
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    after_tomorrow = now + timedelta(days=5)
    employees_obj = Employee.objects.filter(active=True, birth_date__range=[now.strftime("%Y-%m-%d"), after_tomorrow.strftime("%Y-%m-%d")]).order_by("birth_date")
    employees = EmployeeModelSerializer(employees_obj, many=True)
    print(employees_obj)
    return Response({
        "status": "success",
        "code": "200",
        "data": employees.data,
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def employee_view(request: HttpRequest, uuid: str):
    employee_obj = Employee.objects.filter(uuid=uuid)
    if not employee_obj:
        return Response({
            "status": "error",
            "code": "404",
            "data": None
        })
    employee_obj = employee_obj.first()
    employee = EmployeeModelSerializer(employee_obj, many=False)
    return Response({
        "status": "success",
        "code": "200",
        "data": employee.data
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def edit_employee_view(request: HttpRequest, uuid: str):
    data = request.data.dict()
    image = data.pop("image")

    employee_obj = Employee.objects.filter(uuid=uuid)
    if not employee_obj:
        return Response({
            "status": "error",
            "code": "404",
            "data": None
        })
    employee_obj = employee_obj.first()
    employee = CreateEmployeeModelSerializer(employee_obj, data=data)
    if employee.is_valid():
        e = employee.save()
        if ";base64," in image:
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1] 
            e.image =  ContentFile(base64.b64decode(imgstr), name='image.' + ext)
            e.save()
        History.objects.create(
            user=request.user,
            model="Employee",
            comment=f"{e.full_name} tahrirlandi"
        )
    print(employee.errors)
    return Response({
        "status": "success",
        "code": "200",
        "data": employee.data
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def delete_employee_view(request: HttpRequest, uuid: str):
    employee_obj = Employee.objects.filter(uuid=uuid)
    if not employee_obj:
        return Response({
            "status": "error",
            "code": "404",
            "data": None
        })
    employee_obj = employee_obj.first()
    employee_obj.active = False
    employee_obj.save()
    History.objects.create(
        user=request.user,
        model="Employee",
        comment=f"{employee_obj.full_name} o'chirildi"
    )
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def add_employee_view(request: HttpRequest):
    data = request.data.dict()
    format, imgstr = data.pop("image").split(';base64,')
    ext = format.split('/')[-1] 

    image = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
    employee = CreateEmployeeModelSerializer(Employee, data=data)
    if (employee.is_valid()):
        e = employee.create(employee.validated_data)
        e.image = image
        e.save()
        History.objects.create(
            user=request.user,
            model="Employee",
            comment=f"{e.full_name} qo'shildi"
        )
    else:
        print(employee.errors)
        return Response({
            "status": "error",
            "code": "400",
            "data": None
        })
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


# Department
@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def departments_view(request: HttpRequest):
    departments_obj = Department.objects.filter(active=True)
    departments = DepartmentModelSerializer(departments_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": departments.data
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def edit_department_view(request: HttpRequest, pk: int):
    name = request.data.get("name")
    departments_obj = Department.objects.get(pk=pk)
    departments_obj.name = name
    departments_obj.save()
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def add_department_view(request: HttpRequest):
    name = request.data.get("name")
    departments_obj = Department.objects.create(name=name)
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


# Area
@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def areas_view(request: HttpRequest):
    areas_obj = Area.objects.filter(active=True)
    areas = AreaModelSerializer(areas_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": areas.data
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def add_area_view(request: HttpRequest):
    name = request.data.get("name")
    coordinates = request.data.get("coordinates")
    print(name)
    print(coordinates)
    area = Area.objects.create(name=name)
    for coord in coordinates.split(","):
        lat, lon = coord.split("|")
        coordinate = Coordinate.objects.create(latitude=lat, longitude=lon)
        area.coordinates.add(coordinate)
        area.save()
        History.objects.create(
            user=request.user,
            model="Area",
            comment=f"{area.name} qo'shildi"
        )
    print(area)
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def delete_area_view(request: HttpRequest):
    print(request.data)
    area_id = request.data.get("id")
    area = Area.objects.get(pk=area_id)
    area.active = False
    area.save()
    History.objects.create(
        user=request.user,
        model="Area",
        comment=f"{area.name} o'chirildi"
    )
    return Response({
        "status": "success",
        "code": "200",
        "data": None,
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def attendance_view(request: HttpRequest):
    department_pk = int(request.GET.get("department", 0))
    if department_pk > 0:
        employees_obj = Employee.objects.filter(department_id=department_pk, active=True)
        attendance = AttendancesModelSerializer(employees_obj, many=True, context={ "request": request })
        return Response({
            "status": "success",
            "code": "200",
            "data": attendance.data
        })
    employees_obj = Employee.objects.filter(active=True)
    attendance = AttendancesModelSerializer(employees_obj, many=True, context={ "request": request })
    return Response({
        "status": "success",
        "code": "200",
        "data": attendance.data
    })
