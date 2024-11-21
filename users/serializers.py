from rest_framework import serializers

from .models import User, History


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "role", "is_active", )


class HistoryModelSerializer(serializers.ModelSerializer):
    user = UserModelSerializer(User, many=False)
    created = serializers.DateField(format="%d-%m-%Y")

    class Meta:
        model = History
        fields = ("user", "model", "comment", "created", )
