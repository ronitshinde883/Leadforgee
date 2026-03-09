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

from ..serializers.auth_serializers import LoginSerializer, RegisterOwnerSerializer
from ..utils.disable_csrf import CsrfExemptSessionAuthentication

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
            }
        )


class RegisterOwnerView(APIView):
    authentication_classes=[CsrfExemptSessionAuthentication]

    def post(self, request):
        serializer = RegisterOwnerSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.save()
        user = data["user"]
        company = data["company"]

        return Response({
            "message": "Company and owner created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "company": {
                "id": company.id,
                "name": company.title,
                "code": str(company.code)
            }
        })


# REGISTRATION FOR COMPANY OWNERS / NEW USERS WHO CREATE COMPANY DURING REGISTRATION
@csrf_exempt  # FOR TEMPORARY BASIC(DEV) CAN USE PROPER CSRF/AUTH
def register_owner(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        company_name = data.get("company_name")
        domain = data.get("domain")
        phone = data.get("phone")
        country = data.get("country")
        address = data.get("address")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        with transaction.atomic():

            company = Company.objects.create(
                title=company_name,
                domain=domain,
                phone=phone,
                country=country,
                address=address,
            )

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            profile, created = Userprofile.objects.get_or_create(user=user)
            profile.role = "admin"
            profile.company = company
            profile.save()

        return JsonResponse(
            {
                "message": "Company and owner created successfully",
                "company_code": company.code,
            },
            status=201,
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# REGISTRATION FOR EMPLOYEES USING COMPANY CODE
@csrf_exempt  # DEV ONLY NEED CHANGE
def register_employee(request, company_code):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        company = get_object_or_404(Company, code=company_code)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        if not company:
            return JsonResponse(
                {"error": "Unauthorized request, invalid company code"}, status=401
            )

        with transaction.atomic():

            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            profile, created = Userprofile.objects.get_or_create(user=user)
            profile.role = "member"
            profile.company = company
            profile.save()

        return JsonResponse(
            {
                "message": "Created employee user",
                "company": company.title,
                "role": "member",
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# LOGINS USER WITH ANY ROLE
@csrf_exempt  # DEV ONLY NEED CHANGE
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        profile, created = Userprofile.objects.get_or_create(user=user)
        return JsonResponse(
            {
                "message": "Login successfull",
                "username": user.username,
                "role": profile.role,
                "company": profile.company.title,
            },
            status=200,
        )
    else:
        return JsonResponse({"error": "Invalid username or password"}, status=401)


# GETS CURRENT USER
@login_is_required
@csrf_exempt  # TEMP
def get_current_user(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    profile = Userprofile.objects.get(user=request.user)

    return JsonResponse(
        {
            "message": "Current user fetched successfully",
            "username": request.user.username,
            "email": request.user.email,
            "role": profile.role if profile else None,
        }
    )


# LOGOUT FOR ALL USERS
@login_is_required
@csrf_exempt
def logout_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    logout(request)

    return JsonResponse({"message": "User logged out successfully"}, status=200)


@role_required(["admin", "manager"])
@csrf_exempt
def delete_user(request, user_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    curr_profile = Userprofile.objects.filter(user=request.user).first()

    if not curr_profile:
        return JsonResponse({"error": "Profile not found"}, status=403)

    try:
        user_to_delete = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if curr_profile.role != "admin":
        if user_to_delete == request.user:
            return JsonResponse({"error": "You cannot delete yourself"}, status=400)

    if user_to_delete.userprofile.company != curr_profile.company:
        return JsonResponse(
            {"error": "You cannot delete other company users"}, status=400
        )

    user_to_delete.is_active = False
    user_to_delete.save()

    return JsonResponse({"message": "User soft deleted successfully"})


@role_required(["admin"])
@csrf_exempt  # TEMPORARY
def reactivate_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    curr_profile = Userprofile.objects.filter(user=request.user).first()

    if not curr_profile:
        return JsonResponse({"error": "Profile not found"}, status=403)

    try:
        user_to_reactivate = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if user_to_reactivate.userprofile.company != curr_profile.company:
        return JsonResponse(
            {"error": "You cannot reactivate user of other companies"}, status=401
        )

    user_to_reactivate.is_active = True
    user_to_reactivate.save()

    return JsonResponse(
        {
            "message": "User reactivated successfully",
            "username": user_to_reactivate.username,
            "company": user_to_reactivate.userprofile.company.title,
            "role": user_to_reactivate.userprofile.role,
        }
    )


@role_required(["admin"])
@csrf_exempt
def change_roles(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    curr_profile = Userprofile.objects.filter(user=request.user).first()
    if not curr_profile:
        return JsonResponse({"error": "Profile not found"}, status=403)

    data = json.loads(request.body)
    role = data.get("role")
    try:
        if role not in ["admin", "manager", "member"]:
            return JsonResponse({"error": "Role does not exists"}, status=400)

        user_change_role = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exists"}, status=404)

    if user_change_role.userprofile.company != curr_profile.company:
        return JsonResponse(
            {"error": "You cannot change the role of another company's user"},
            status=401,
        )

    user_change_role.userprofile.role = role
    user_change_role.save()

    return JsonResponse(
        {
            "message": "User role changed successfully",
            "username": user_change_role.username,
            "company": user_change_role.userprofile.company.title,
            "role": user_change_role.userprofile.role,
        }
    )


@login_is_required
@require_http_methods(["POST"])
@csrf_exempt
def change_password(request):

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    data = json.loads(request.body)
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return JsonResponse({"error": "Both password required"}, status=400)

    user = authenticate(request, username=request.user.username, password=old_password)

    if not user:
        return JsonResponse({"error": "Invalid old password"}, status=400)

    user.set_password(new_password)
    user.save()

    return JsonResponse(
        {
            "message": "Password changed successfully",
        }
    )
