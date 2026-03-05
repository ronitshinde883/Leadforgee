from django.db import models
from django.contrib.auth.models import User

from .common import Company


class Contact(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_index=True, related_name="contacts"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
        related_name="owned_contacts",
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"], name="unique_contact_email_per_company"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
