from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.activity import ActivityLog
from ..utils.disable_csrf import CsrfExemptSessionAuthentication

class ActivityLogView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[CsrfExemptSessionAuthentication]

    def get(self, request):
        company = request.user.userprofile.company

        logs = ActivityLog.objects.filter(
            company=company
        ).select_related("user")[:50]

        data = []

        for log in logs:
            data.append({
                "user": log.user.username,
                "action": log.action,
                "description": log.description,
                "related_type": log.content_type.model,
                "related_id": log.object_id,
                "created_at": log.created_at
            })

        return Response({
            "message": "Acitivity log fetched successfully",
            "data": data
        })