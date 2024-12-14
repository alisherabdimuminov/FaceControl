
import base64
from datetime import datetime
from shapely.geometry import Polygon, Point
from deepface import DeepFace

from django.http import HttpRequest
from rest_framework import decorators
from rest_framework.response import Response
from django.core.files.base import ContentFile

from employees.models import Area, Employee, AccessControl, OutputControl


@decorators.api_view(http_method_names=["POST"])
def check_location(request: HttpRequest):
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")
    print("latitude:", latitude)
    print("logitude:", longitude)

    areas = Area.objects.filter(active=True)
    print(areas)
    for area in areas:
        coordinates = []
        for coord in area.coordinates.all():
            coordinates.append((coord.latitude, coord.longitude))
        polygon = Polygon(coordinates)
        point = Point((latitude, longitude))
        point_in_the_area = polygon.contains(point)
        print(polygon)
        print(point)
        print(point_in_the_area)
        if (point_in_the_area):
            return Response({
                "status": "success",
                "code": "200",
                "data": area.pk
            })
    return Response({
        "status": "error",
        "code": "404",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
def check_passport(request: HttpRequest):
    passport = request.data.get("passport", "").lower()
    employee = Employee.objects.filter(handle__icontains=passport)
    if employee:
        employee = employee.first()
        return Response({
            "status": "success",
            "code": "200",
            "data": employee.pk
        })
    return Response({
        "status": "error",
        "code": "404",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
def faceid(request: HttpRequest):
    now = datetime.now()
    base64data = request.data.get("image")
    passport = request.data.get("passport", "").lower()
    employee = Employee.objects.filter(handle__icontains=passport)
    format, imgstr = base64data.split(';base64,')
    ext = format.split('/')[-1]
    base64image = ContentFile(base64.b64decode(imgstr), name=f"taken.{ext}")
    if employee:
        employee = employee.first()
        print(now)
        if (now.hour) < 12:
            control = AccessControl.objects.filter(employee=employee.pk, created__day=now.day, created__month=now.month, created__year=now.year, status="arrived")
            if control:
                return Response({
                    "status": "error",
                    "code": "201",
                    "data": None
                })
            control = AccessControl.objects.create(
                employee=employee,
                image=base64image,
                longitude="12",
                latitude="234",
                area=Area.objects.first(),
            )
            try:
                result = DeepFace.verify(
                    img1_path=employee.image.path,
                    img2_path=control.image.path,
                )
                print(result)
                if result.get("verified"):
                    if now.hour >= 9:
                        control.status = "late"
                    else:
                        if now.hour == 8 and now.minute > 45:
                            control.status = "late"
                        else:
                            control.status = "arrived"
                    control.save()
                else:
                    control.status = "failed"
                    control.save()
                return Response({
                    "status": "success",
                    "code": "200",
                    "data": result.get("verified")
                })
            except:
                return Response({
                    "status": "error",
                    "code": "400",
                    "data": None
                })
        else:
            control = OutputControl.objects.filter(employee=employee.pk, created__day=now.day, created__month=now.month, created__year=now.year, status="arrived")
            if control:
                return Response({
                    "status": "error",
                    "code": "201",
                    "data": None
                })
            control = OutputControl.objects.create(
                employee=employee,
                image=base64image,
                longitude="12",
                latitude="234",
                area=Area.objects.first(),
            )
            try:
                result = DeepFace.verify(
                    img1_path=employee.image.path,
                    img2_path=control.image.path
                )
                print(result)
                if result.get("verified"):
                    control.status = "arrived"
                    control.save()
                else:
                    control.status = "failed"
                    control.save()
                return Response({
                    "status": "success",
                    "code": "200",
                    "data": result.get("verified")
                })
            except:
                return Response({
                    "status": "error",
                    "code": "400",
                    "data": None
                })
    return Response({
        "status": "error",
        "code": "404",
        "data": None
    })
