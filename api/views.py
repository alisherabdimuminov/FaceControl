
import base64
from datetime import datetime
from shapely.geometry import Polygon, Point
from deepface import DeepFace
from docxtpl import DocxTemplate

from django.http import HttpRequest
from rest_framework import decorators
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.db.models import Q

from employees.models import Area, Employee, AccessControl, OutputControl


@decorators.api_view(http_method_names=["POST"])
def make_word(request: HttpRequest):
    data = request.data.get("data")
    doc = DocxTemplate("example.docx")
    context = { 'users' : data }
    doc.render(context)
    doc.save("media/generated_doc.docx")
    return Response({
        "status": "success",
        "code": "200",
        "data": request.build_absolute_uri("media/generated_doc.docx")
    })



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
    passport = request.data.get("passport", "").upper()
    area = request.data.get("area")
    if not passport:
        return Response({
            "status": "success",
            "code": "404",
            "data": None
        })
    employee = Employee.objects.filter(handle=passport)
    format, imgstr = base64data.split(';base64,')
    ext = format.split('/')[-1]
    base64image = ContentFile(base64.b64decode(imgstr), name=f"taken.{ext}")
    if employee:
        employee = employee.first()
        if (now.hour) < 12:
            control = AccessControl.objects.filter(Q(status="arrived") | Q(status="late"), employee=employee.pk, created__day=now.day, created__month=now.month, created__year=now.year)
            print(control)
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
                anti_spoofing = DeepFace.extract_faces(
                    img_path=control.image.path,
                    anti_spoofing=True
                )
                print(result)
                if result.get("verified"):
                    if not anti_spoofing[0].get("is_real"):
                        control.status = "failed"
                        control.save()
                        return Response({
                            "status": "error",
                            "code": "300",
                            "data": None
                        })
                    if now.hour >= 9:
                        control.status = "late"
                    else:
                        if now.hour == 8 and now.minute > 45:
                            control.status = "late"
                        else:
                            control.status = "arrived"
                    control.save()
                    return Response({
                        "status": "success",
                        "code": "200",
                        "data": result.get("verified")
                    })
                else:
                    control.status = "failed"
                    control.save()
                    return Response({
                        "status": "error",
                        "code": "402",
                        "data": result.get("verified")
                    })
            except:
                control.status = "failed"
                control.save()
                return Response({
                    "status": "error",
                    "code": "400",
                    "data": "None"
                })
        else:
            control = OutputControl.objects.filter(employee=employee.pk, created__day=now.day, created__month=now.month, created__year=now.year, status="gone")
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
                anti_spoofing = DeepFace.extract_faces(
                    img_path=control.image.path,
                    anti_spoofing=True
                )
                print(result)
                print(anti_spoofing)
                if result.get("verified"):
                    control.status = "gone"
                    control.save()
                    return Response({
                        "status": "success",
                        "code": "200",
                        "data": result.get("verified")
                    })
                else:
                    control.status = "failed"
                    control.save()
                    return Response({
                        "status": "error",
                        "code": "402",
                        "data": result.get("verified")
                    })
            except Exception as e:
                print(e)
                control.status = "failed"
                control.save()
                return Response({
                    "status": "error",
                    "code": "400",
                    "data": "none"
                })
    return Response({
        "status": "error",
        "code": "404",
        "data": None
    })
