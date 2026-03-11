import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from ..decorators import role_required, login_is_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models.common import Company
from ..models.user import Userprofile


"""
  ****REMOVE @csrf_exempt BEFORE DEPLOYING*****

  THINGS TO DO
  1. NEED TO SHIFT TO CBV(CLASS BASED VIEWS) AFTER CREATING MORE API FUNCTIONS/CONTROLLERS
  2. USE JWT OR SESSION API FOR AUTH SYSTEMS
  3. ADD VERIFICATION AND FORGOT PASSWORD TOKENS
  4. CREATING, INVITE LINKS AND INVITE MODEL 
  5. REGISTERING MEMBERS BASED ON INVITE LINKS
  6. IF COMPANY IS_ACTIVE FIELD IS FALSE PREVENT USERS FROM LOGGING IN AND REGISTERING
"""

"""
    SWITCHING TOO DRF AND CLASS-BASED VIEWS
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializers.auth_serializers import (
    LoginSerializer,
    RegisterOwnerSerializer,
    RegisterEmployeeSerializer,
    ChangePasswordSerializer,
)
from ..utils.disable_csrf import CsrfExemptSessionAuthentication
from ..utils.permissions import IsCompanyAdmin


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]

        login(request, user)  # creates session

        return Response(
            {
                "message": "Logged in successfully",
                "user_id": user.id,
                "name": user.username,
                "role": user.userprofile.role,
            },
            status=200,
        )


class RegisterOwnerView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request):
        serializer = RegisterOwnerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.save()
        user = data["user"]
        company = data["company"]

        return Response(
            {
                "message": "Company and owner created successfully",
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "company": {
                    "id": company.id,
                    "name": company.title,
                    "code": str(company.code),
                },
            },
            status=201,
        )


class RegisterEmployeeView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request):
        serializer = RegisterEmployeeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.save()
        user = data["user"]
        company = data["company"]

        return Response(
            {
                "message": "Company and owner created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.userprofile.role,
                },
                "company": {
                    "id": company.id,
                    "name": company.title,
                    "code": str(company.code),
                },
            },
            status=201,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        company = profile.company

        return Response(
            {
                "message": "Current user details fetched successfully",
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": profile.role,
                "avatar": profile.avatar,
                "isEmailVerified": profile.is_emailverified,
                "company": {
                    "id": company.id,
                    "name": company.title,
                    "domain": company.domain,
                },
            },
            status=200,
        )

class LogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        logout(request)

        return Response({"message": "User logged out successfully"}, status=200)
    

class ChangePasswordView(APIView):
    authentication_classes=[CsrfExemptSessionAuthentication]
    permission_classes=[IsAuthenticated]

    def patch(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        user = request.user

        # check old password
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({
                "error": "Old password is invalid",
            }, status=400)

        # set new password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({
            "message": "Password changed successfully",
            "username": user.username,
            "company": user.userprofile.company.title,
            "role": user.userprofile.role,
        })

"""
---------------------- USER MANAGEMENT VIEWS ----------------------
"""    
class UpdateUserRoleView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    authentication_classes=[CsrfExemptSessionAuthentication]

    def patch(self, request, id):
        curr_profile = request.user.userprofile

        # check if admin
        if curr_profile.role != "admin":
            return Response({"error": "Only admins can access this page"}, status=403)
        
        try:
            profile = Userprofile.objects.select_related("user").get(user_id=id, company=curr_profile.company)
        except Userprofile.DoesNotExist:
            return Response({
                "error": "User profile does not exists",
            }, status=404)
        
        new_role = request.data.get("role")

        if new_role not in ["admin", "manager", "member"]:
            return Response({"error": "Invalid role"}, status=400)
        
        profile.role = new_role
        profile.save()

        return Response({
            "message": "Role updated successfully",
            "user": profile.user.username,
            "role": profile.role
        })

class RemoveCompanyUserView(APIView):
    permission_classes=[IsAuthenticated, IsCompanyAdmin]
    authentication_classes=[CsrfExemptSessionAuthentication]

    def delete(self, request, id):
        curr_profile = request.user.userprofile
        
        # check if admin
        if curr_profile.role != "admin":
            return Response({"error": "Only admins can access this page"}, status=403)

        try:
            profile = Userprofile.objects.select_related("user").get(user_id=id, company=curr_profile.company)
        except Userprofile.DoesNotExist:
            return Response({
                "error": "User profile does not exists",
            }, status=404)

        # prevent deleting urself
        if request.user == profile.user:
            return Response({"error": "You cannot remove yourself"}, status=400)
        
        profile.user.is_active = False
        
        return Response({"message": "User removed successfully"}, status=200)
    

class CompanyUsersView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        company = profile.company

        if profile.role != "admin":
            return Response({"error": "Only admins can view this page"}, status=403)

        users = Userprofile.objects.filter(company=company).select_related("user")

        data = []

        for p in users:
            u = p.user
            data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "last_login": u.last_login,
                "role": p.role,
            })
        
        return Response({
            "message": "Company users fetched successfullly",
            "company_name": company.title,
            "users": data
        }, status=200)

