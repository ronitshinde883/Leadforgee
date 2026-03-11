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
4. AFTER COMPANY IS SET TO IS_ACTIVE FALSE USERS, LEADS, CONTACT, DEALS, TASKS SHOULD ALSO BE SOFT DELETED
"""

"""
    SWITCHING TOO DRF AND CLASS-BASED VIEWS
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers.company_serializers import CompanySerializer
from ..utils.disable_csrf import CsrfExemptSessionAuthentication

class CompanyAPIView(APIView):
    authentication_classes=[CsrfExemptSessionAuthentication]
    permission_classes=[IsAuthenticated]

    # GET /api/company/ 
    def get(self, request):
        company = request.user.userprofile.company

        if company.is_active == False:
            return Response({"error": "Company does not exists"}, status=404)

        data = {
            "id": company.id,
            "name": company.title,
            "domain": company.domain,
            "phone": company.phone,
            "address": company.address,
            "country": company.country,
            "created_at": company.created_at,
        }

        return Response({"message": "Company details fetched successfully", "data": data}, status=200);

    def patch(self, request):
        company = request.user.userprofile.company
        serializer = CompanySerializer(company, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        profile = request.user.userprofile

        if profile.role != "admin":
            return Response({
                "error": "Only admins can delete the company"
            }, status=403)
        
        company = profile.company
        company.is_active = False
        company.save()

        return Response({
            "message": "Successfully deleted the company"
        }, status=200)

"""
    REACTIVATE COMPANY VIEW MISSING
"""