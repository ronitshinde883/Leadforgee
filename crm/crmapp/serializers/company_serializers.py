from rest_framework import serializers
from ..models.common import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = [
            "code",
            "is_active",
            "created_at"
        ]
    
    def validate_domain(self, value):
        if Company.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Company domain already exists")
        return value
    
    def validate_name(self, value):
        if Company.objects.filter(title=value).exists():
            raise serializers.ValidationError("Company title already exists")
        return value