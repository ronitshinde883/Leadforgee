from ..models.task import Task
from django.contrib.contenttypes.models import ContentType

"""
    SWITCHING TOO DRF AND CLASS-BASED VIEWS
"""
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializers.task_serializers import TaskSerializer
from ..utils.disable_csrf import CsrfExemptSessionAuthentication
from ..services.activity_service import log_activity


# TASK VIEWS
class TaskViewSet(ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_field = "id"

    # filtering fields (LATER)
    filterset_fields = ["status"]
    search_fields = ["title"]
    ordering_fields = ["duedate", "created_at"]

    def get_queryset(self):
        user = self.request.user
        company = user.userprofile.company
        return Task.objects.filter(company=company).select_related(
            "assigned_by", "company"
        )

    # GET /api/tasks/
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # GET /api/tasks/{id}
    def retrieve(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            task = Task.objects.get(id=id, company=company)
        except Task.DoesNotExist:
            return Response({"error": "Task does not exists"}, status=404)

        serializer = TaskSerializer(task)

        return Response(
            {
                "message": "Fetched task successfully",
                "task": serializer.data,
                # "assignedTo": task.assigned_to.username
            },
            status=200,
        )

    """
        NEED TO ADD VALIDATION CHECKS TO MAKE SURE IF THE TASK ASSIGNED FOR THE MODEL IS IN THAT COMPANY OR NOT, ALSO IF IT EXISTS OR NOT
    """
    # POST /api/tasks/
    def create(self, request):
        user = request.user
        company = user.userprofile.company

        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            task = serializer.save(
                assigned_by=user,
                company=company,
                status="pending",
            )
            log_activity(
                user=user,
                company=company,
                action="create",
                obj=task,
                description=f"Created {task.title} task",
            )

            return Response(
                {"message": "Created task successfully", "task_id": task.id}, status=201
            )

        return Response(serializer.errors, status=400)

    # PATCH /api/tasks/{id}
    def partial_update(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            task = Task.objects.get(id=id, company=company)
        except Task.DoesNotExist:
            return Response({"error": "Lead does not exists"}, status=404)

        serializer = TaskSerializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated successfully"})

        return Response(serializer.errors, status=400)

    # LATER
    def update(self, request, id=None):
        pass

    # DELETE /api/tasks/{id}
    def destroy(self, request, id=None):
        user = request.user
        company = user.userprofile.company

        try:
            task = Task.objects.get(id=id, company=company)
        except Task.DoesNotExist:
            return Response({"error": "Lead does not exists"}, status=404)

        task.delete()

        return Response({"message": "Task deleted successfully"}, status=200)


"""
@login_is_required
@csrf_exempt
def create_task(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)

        model_name = data.get("model_name")
        object_id = data.get("object_id")
        assigned_to_id = data.get("assigned_to")
        description = data.get("description")
        duedate = data.get("duedate")
        status = data.get("status", "pending")

        if not model_name or not object_id or not description or not duedate:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        
        ALLOWED_MODELS = {
            "deal": Deal,
            "lead": Lead,
            "contact": Contact,
        }

        model_class = ALLOWED_MODELS.get(model_name.lower())
        if not model_class:
            return JsonResponse({"error": "Invalid model name"}, status=400)

        try:
            related_object = model_class.objects.get(id=object_id)
        except model_class.DoesNotExist:
            return JsonResponse({"error": "Related object not found"}, status=404)

        user_company = request.user.userprofile.company
        if related_object.company != user_company:
            return JsonResponse({"error": "Unauthorized company access"}, status=403)

        content_type = ContentType.objects.get_for_model(model_class)

        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Assigned user not found"}, status=404)

        parsed_date = parse_date(duedate)
        if not parsed_date:
            return JsonResponse({"error": "Invalid date format (YYYY-MM-DD required)"}, status=400)

        task = Task.objects.create(
            company=user_company,
            assignedTo=assigned_to,
            assignedBy=request.user,
            content_type=content_type,
            object_id=object_id,
            description=description,
            duedate=parsed_date,
            status=status
        )

        return JsonResponse({"message": "Task created successfully"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
"""
