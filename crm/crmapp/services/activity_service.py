from django.contrib.contenttypes.models import ContentType
from crmapp.models.activity import ActivityLog

def log_activity(user, company, action, obj, description=""):
    ActivityLog.objects.create(
        user=user,
        company=company,
        action=action,
        description=description,
        content_type=ContentType.objects.get_for_model(obj),
        object_id = obj.id
    )