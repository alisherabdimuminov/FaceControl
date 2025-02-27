import base64
from io import BytesIO
from openpyxl import Workbook
from datetime import datetime, timedelta

from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework import decorators
from rest_framework import permissions
from django.core.files.base import ContentFile
from django.db.models import Q, Func, F, Value, CharField
from django.db.models.functions import ExtractMonth, ExtractDay

from users.models import History
from .models import (
    Coordinate,
    Area,
    Employee,
    Department,
    AccessControl,
    WorkTime,
)
from .serializers import (
    CoordinateModelSerializer,
    AreaModelSerializer,
    EmployeeModelSerializer,
    DepartmentModelSerializer,
    CreateEmployeeModelSerializer,
    AttendancesModelSerializer,
    AttendancesSerializer,
    WorkTimeModelSerializer,
)


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def work_times_view(request: HttpRequest):
    work_times_obj = WorkTime.objects.all()
    work_times = WorkTimeModelSerializer(work_times_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": work_times.data
    })


# Employee
@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def employees_view(request: HttpRequest):
    department_pk = request.GET.get("department") or 0
    if department_pk == 0 or department_pk == "0":
        employees_obj = Employee.objects.filter(active=True).order_by("full_name")
        employees = EmployeeModelSerializer(employees_obj, many=True)
    else:
        department = Department.objects.get(pk=department_pk)
        employees_obj = Employee.objects.filter(active=True, department=department).order_by("full_name")
        employees = EmployeeModelSerializer(employees_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": employees.data,
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def employees_birth_date_view(request: HttpRequest):
    now = datetime.now()
    # Current date
    current_date = now.date()
    end_date = current_date + timedelta(days=7)

    # End date (5 days from now)
    end_date = current_date + timedelta(days=5)

    employees_obj = Employee.objects.filter(
        birth_date__month__range=(current_date.month, end_date.month),
        birth_date__day__range=(current_date.day, end_date.day),
        active=True
    )
    employees = EmployeeModelSerializer(employees_obj, many=True)
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
# @decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
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
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def delete_area_view(request: HttpRequest):
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
    department_pk = int(request.GET.get("department", 1))
    if department_pk > 0:
        employees_obj = Employee.objects.filter(department_id=department_pk, active=True).order_by("full_name")
        attendance = AttendancesModelSerializer(employees_obj, many=True, context={ "request": request })
        return Response({
            "status": "success",
            "code": "200",
            "data": attendance.data
        })
    employees_obj = Employee.objects.filter(active=True).order_by("full_name")
    attendance = AttendancesModelSerializer(employees_obj, many=True, context={ "request": request })
    return Response({
        "status": "success",
        "code": "200",
        "data": attendance.data
    })



@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def reports(request: HttpRequest):
    now = datetime.now()
    department = request.data.get("department") or 1
    start_day = request.data.get("start_day")
    start_month = request.data.get("start_month")
    start_year = request.data.get("start_year")
    end_day = request.data.get("end_day")
    end_month = request.data.get("end_month")
    end_year = request.data.get("end_year")

    employees_obj = Employee.objects.filter(department_id=department, active=True).order_by("full_name")

    start_date = datetime.strptime(f"{start_day}-{start_month}-{start_year}", "%d-%m-%Y")
    end_date = datetime.strptime(f"{end_day}-{end_month}-{end_year}", "%d-%m-%Y")

    date_range = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") 
                  for i in range((end_date - start_date).days + 1)]

    response = {}

    for date in date_range:
        day, month, year = date.split("-")
        report = AttendancesSerializer(employees_obj, many=True, context={ "date": { "day": day, "month": month, "year": year } })
        response[date] = report.data

    return Response({
        "status": "success",
        "code": "200",
        "data": response
    })


@decorators.api_view(http_method_names=["GET"])
# @decorators.permission_classes(permission_classes=[permissions.IsAuthenticated])
def reports_as_xlsx(request: HttpRequest):
    now = datetime.now()
    department = request.GET.get("department") or 1
    start_day = request.GET.get("start_day")
    start_month = request.GET.get("start_month")
    start_year = request.GET.get("start_year")
    end_day = request.GET.get("end_day")
    end_month = request.GET.get("end_month")
    end_year = request.GET.get("end_year")

    employees_obj = Employee.objects.filter(department_id=department, active=True).order_by("full_name")
    department = Department.objects.get(pk=department)

    start_date = datetime.strptime(f"{start_day}-{start_month}-{start_year}", "%d-%m-%Y")
    end_date = datetime.strptime(f"{end_day}-{end_month}-{end_year}", "%d-%m-%Y")

    date_range = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") 
                  for i in range((end_date - start_date).days + 1)]

    wb = Workbook()
    ws = wb.active

    ws.title = department.name

    data = []
    data.append(["Familiya Ism Sharifi", ] + date_range)

    response = {}

    for date in date_range:
        day, month, year = date.split("-")
        report = AttendancesSerializer(employees_obj, many=True, context={ "date": { "day": day, "month": month, "year": year } })
        response[date] = report.data

    counter = 0
    for e in employees_obj:
        k = []
        for r in response:
            k.append(response[r][counter].get("attendance_access_time"))
        data.append([f"{e.full_name}", ] + k)
        counter += 1


    ws.append(data[0])

    for i, row in enumerate(data[1:], start=2):
        ws.append(row)
        # last_data_column = len(data[0]) - 2
        # ws[f"{chr(65 + last_data_column + 1)}{i}"] = f"=SUM(B{i}:{chr(65 + last_data_column)}{i})"

    file_stream = BytesIO()
    wb.save(file_stream)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{department.name}.xlsx"'
    response.write(file_stream.getvalue())
    return response


@decorators.api_view(http_method_names=["GET"])
def statistics(request: HttpRequest):
    now = datetime.now()
    departments = Department.objects.filter(active=True)
    data = []
    for department in departments:
        employees_obj = Employee.objects.filter(department=department)
        access_arrived_obj = AccessControl.objects.filter(employee__department=department, created__year=now.year, created__month=now.month, created__day=now.day, status="arrived")
        access_late_obj = AccessControl.objects.filter(employee__department=department, created__year=now.year, created__month=now.month, created__day=now.day, status="late")
        data.append({
            "department": department.name,
            "all": employees_obj.count(),
            "arrived": access_arrived_obj.count(),
            "late": access_late_obj.count(),
            "didnotcome": employees_obj.count() - (access_arrived_obj.count() + access_late_obj.count()),
        })
    return Response({
        "status": "success",
        "code": "200",
        "data": data
    })
