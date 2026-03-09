from rest_framework import serializers
from ..models import Task

"""
    1. Add status later to read-only fields after creating a function to update the status of the task
    2. Add more validation
    3. Change the fields from "__all__" to an array of fields
"""

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = [
            "company",
            "assigned_by",
            "created_at",
            "related_object",
            "content_type",
            "object_id"
        ]