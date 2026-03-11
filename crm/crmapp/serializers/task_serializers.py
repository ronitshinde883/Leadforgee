from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from ..models import Task

"""
    1. Add status later to read-only fields after creating a function to update the status of the task
    2. Add more validation
    3. Change the fields from "__all__" to an array of fields
"""

MODEL_MAP = {
    "lead": "lead",
    "contact": "contact",
    "deal": "deal"
}

class TaskSerializer(serializers.ModelSerializer):
    related_to = serializers.CharField(write_only=True)
    related_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "duedate",  # change to due_date
            "assigned_to",
            "related_to",
            "related_id",
            "attachement",
            "created_at"
        ]

    def validate(self, data):
        related_to = data.get("related_to")

        if related_to not in MODEL_MAP:
            raise serializers.ValidationError(
                {"related_to": "Invalid related model"}
            )
        
        return data
    
    def create(self, validated_data):
        related_to = validated_data.pop("related_to")
        related_id = validated_data.pop("related_id")

        content_type = ContentType.objects.get(
            app_label="crmapp",
            model=MODEL_MAP[related_to]
        )

        validated_data["content_type"] = content_type
        validated_data["object_id"] = related_id

        return super().create(validated_data)