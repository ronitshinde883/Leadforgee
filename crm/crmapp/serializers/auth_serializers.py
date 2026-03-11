from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

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
    password = serializers.CharField(write_only=True)   # can add validators=[validate_password]

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        data["user"] = user
        return data

class BaseRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)   # can add validators=[validate_password]
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

class RegisterOwnerSerializer(BaseRegisterSerializer):
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
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
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
    
class RegisterEmployeeSerializer(BaseRegisterSerializer):
    code = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        code = validated_data.pop("code")

        try:
            company = Company.objects.get(code=code)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid invite code")
        
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Userprofile.objects.create(
            user=user,
            company=company,
            role="member"
        )

        return {
            "user": user,
            "company": company
        }
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True)   # validators=[validate_password]
    