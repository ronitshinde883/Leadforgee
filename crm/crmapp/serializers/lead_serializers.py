from rest_framework import serializers
from ..models import Lead

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = [
            "company",
            "owner",
            "created_at",
            "updated_at",
            "is_archived",
            "converted_at"
        ]