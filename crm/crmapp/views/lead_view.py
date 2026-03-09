from ..services.lead_service import convert_lead
from ..services.lead_service import (
    LeadAlreadyConvertedException,
    ContactAlreadyExistsException,
)
from ..models.lead import Lead
from ..utils.disable_csrf import CsrfExemptSessionAuthentication

"""
    SWITCHING TOO DRF AND CLASS-BASED VIEWS
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models.lead import Lead
from ..serializers.lead_serializers import LeadSerializer

"""
    1. Convert Lead
        @action(detail=True, methods=["post"])
        def convert:
    2. Pagination
    3. Add advance filtering
        ?value__gte=5000
        ?created_at__gte=2025-01-01
        ?created_at__lte=2025-12-31
    4. permission logic
    5. Lead statistics endpoint (api/leads/stats/)
"""

class LeadViewSet(ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    # filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]   INTEGRATED THIS IN SETTINGS DIRECTLY
    permission_classes = [IsAuthenticated]
    serializer_class = LeadSerializer
    lookup_field = "id"

    # filtering fields
    filterset_fields = ["status", "source"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["value", "created_at"]

    def get_queryset(self):
        user = self.request.user
        company = user.userprofile.company
        return (Lead.objects
            .filter(company=company, is_archived=False)
            .select_related("owner", "company")
        )

    # GET /api/leads/
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # GET /api/leads/{id}/
    def retrieve(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            lead = Lead.objects.get(id=id, company=company, is_archived=False)
        except Lead.DoesNotExist:
            return Response(
                {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadSerializer(lead)
        return Response(
            {"message": "Fetched lead successfully", "lead": serializer.data}
        )

    # POST /api/leads/
    def create(self, request):
        user = request.user
        company = user.userprofile.company

        serializer = LeadSerializer(data=request.data)

        if serializer.is_valid():
            lead = serializer.save(owner=user, company=company, status="new")

            return Response(
                {"message": "Created lead successfully", "lead_id": lead.id},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /api/leads/{id}/
    def partial_update(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            lead = Lead.objects.get(id=id, company=company)
        except Lead.DoesNotExist:
            return Response(
                {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadSerializer(lead, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Lead updated successfully"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT /api/leads/{id}/
    def update(self, request, id=None):
        pass

    # DELETE /api/leads/{id}/
    def destroy(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            lead = Lead.objects.get(id=id, company=company, is_archived=False)
        except Lead.DoesNotExist:
            return Response(
                {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
            )

        lead.is_archived = True
        lead.save()

        return Response(
            {"message": "Lead delete successfully"}, status=status.HTTP_200_OK
        )
