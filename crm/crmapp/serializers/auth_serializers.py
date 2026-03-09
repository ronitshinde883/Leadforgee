from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers

from ..models.common import Company
from ..models.user import Userprofile
from .company_serializers import CompanySerializer


"""
***TO BE DONE LATER***
class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

class RegisterOwnerResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    company = CompanySerializer()
"""


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        data["user"] = user
        return data

class RegisterOwnerSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    company = CompanySerializer()

    @transaction.atomic
    def create(self, validated_data):
        company_data = validated_data.pop("company")

        # create company
        company = Company.objects.create(**company_data)

        # create user
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"]
        )

        # create user profile
        Userprofile.objects.create(
            user=user,
            company=company,
            role="admin"
        )

        return {
            "user": user,
            "company": company
        }
    