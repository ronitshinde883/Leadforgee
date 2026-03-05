from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
import json
from ..models.common import Company
from ..models.user import Userprofile
from ..decorators import role_required, login_is_required

"""
1. IF IS_ACTIVE FIELD IS FALSE THEN DO NOT PERFORM COMPANY ACTIONS
2. ADD MORE FUNCTIONALITIES IN COMPANY VIEWS
3. ADD PASSWORD CONFIRMATION AND EMAIL VERIFICATION DURING COMPANY EDITING
"""

@login_is_required
@csrf_exempt
def get_all_users(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    profile = request.user.userprofile
    company = profile.company

    members = Userprofile.objects.filter(company=company, user__is_active=True)  # DOUBT

    data = []
    for m in members:
        data.append(
            {"username": m.user.username, "email": m.user.email, "role": m.role}
        )

    return JsonResponse({"message": "Company users fetched successfully", "data": data})

@login_is_required
@require_http_methods(["GET"])
@csrf_exempt
def get_company(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"})

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    profile = request.user.userprofile
    company = profile.company

    return JsonResponse(
        {
            "message": "Company fetched successfully",
            "title": company.title,
            "code": company.code,
            "created_at": company.created_at,
        }
    )

@login_is_required
@role_required(["admin"])
@csrf_exempt
def update_company(request):
    if not request.method != "PATCH":
        return JsonResponse({"error": "PATCH request required"}, status=405)

    profile = request.user.userprofile
    company = profile.company

    data = json.loads(request.body)

    allowed_fields = ["title", "domain", "phone", "country", "address"]

    for field in allowed_fields:
        if field in data:
            setattr(company, field, data[field])

    company.save()

    return JsonResponse({"message": "Updated company details successfully"})

@login_is_required
@role_required(["admin"])
@csrf_exempt
def delete_company(request):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=405)

    profile = request.user.userprofile
    company = profile.company

    if not company.is_active:
        return JsonResponse({"error": "Company already deactivated"}, status=400)

    data = json.loads(request.body)
    password = data.get("password")
    if not password:
        return JsonResponse({"error": "Password is required"}, status=400)

    is_verified = authenticate(
        request, username=request.user.username, password=password
    )
    if not is_verified:
        return JsonResponse({"error": "Unauthorized access"}, status=401)

    company.is_active = False
    company.save()

    return JsonResponse({"message": "Company soft deleted successfully"})

@login_is_required
@role_required(["admin"])
@csrf_exempt
def reactivate_company(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    profile = request.user.userprofile
    company = profile.company

    company.is_active = True
    company.save()

    return JsonResponse({"message": "Company reactivated successfully"})
