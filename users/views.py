from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import decorators
from rest_framework import permissions

from .models import User, History
from .serializers import (
    HistoryModelSerializer,
    UserModelSerializer,
)


@decorators.api_view(http_method_names=["POST"])
def login(request: HttpRequest):
    username = request.data.get("username", "")
    password = request.data.get("password", "")

    user = User.objects.filter(username=username)
    
    if not user:
        return Response({
            "status": "error",
            "code": "username_not_found",
            "data": None
        })
    
    user = user.first()

    if not user.check_password(raw_password=password):
        return Response({
            "status": "error",
            "code": "invalid_password",
            "data": None
        })
    
    token = Token.objects.get_or_create(user=user)
    History.objects.create(
        user=user,
        model="User",
        comment="Login with username/password"
    )
    return Response({
        "status": "success",
        "code": "200",
        "data": {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "token": token[0].key
        }
    })

@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated, ])
def profile(request: HttpRequest):
    user: User = request.user
    token = request.headers.get("authorization", "1 2").split(" ")[-1]

    if not user.is_active:
        return Response({
            "status": "error",
            "code": "user_is_not_active",
            "data": None
        })
    
    return Response({
        "status": "success",
        "code": "200",
        "data": {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "token": token
        }
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated, ])
def users(request: HttpRequest):
    users_obj = User.objects.all()
    users = UserModelSerializer(users_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": users.data
    })

@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated, ])
def toggle_user_active(request: HttpRequest):
    user_id = request.data.get("id")
    user = User.objects.get(pk=user_id)
    if (user.is_active):
        user.is_active = False
        user.save()
        History.objects.create(
            user=request.user,
            model="User",
            comment="Change user active status to False"
        )
    else:
        user.is_active = True
        user.save()
        History.objects.create(
            user=request.user,
            model="User",
            comment="Change user active status to True"
        )
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["POST"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated, ])
def change_password(request: HttpRequest):
    user_id = request.data.get("id")
    password = request.data.get("password")
    user = User.objects.get(pk=user_id)
    user.set_password(raw_password=password)
    user.save()
    History.objects.create(
        user=request.user,
        model="User",
        comment="Change user password"
    )
    return Response({
        "status": "success",
        "code": "200",
        "data": None
    })


@decorators.api_view(http_method_names=["GET"])
@decorators.permission_classes(permission_classes=[permissions.IsAuthenticated, ])
def histories(request: HttpRequest):
    histories_obj = History.objects.all()
    histories = HistoryModelSerializer(histories_obj, many=True)
    return Response({
        "status": "success",
        "code": "200",
        "data": histories.data
    })
