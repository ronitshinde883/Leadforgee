from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from .common import Company


class Task(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_index=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned",
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_created",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")
    STATUS_CHOICE = [
        ("pending", "Pending"),
        ("in-progress", "In-progress"),
        ("completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="pending", db_index=True
    )
    # change to due_date
    duedate = models.DateField(db_index=True)
    attachement = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=128)  # NULL TO BE REMOVED LATER
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["duedate"]
        indexes = [
            models.Index(fields=["content_type", "                                                                                                            "]),
            models.Index(fields=["company", "status"]),
        ]

    def clean(self):
        if self.related_object and self.related_object.company != self.company:
            raise ValidationError("Related object must belong to the same company")
