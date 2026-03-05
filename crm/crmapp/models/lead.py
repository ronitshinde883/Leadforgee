from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .common import Company
from .contact import Contact

"""
1. RATHER THAN USING STATUS 'CONVERTED' WE CAN USE A CONVERT() UTIL METHOD, WHICH WILL;
    CREATE CONTACT -> SETS CONVERTED_AT -> SETS STATUS == CONVERTED -> LEAD.SAVE()
"""


class Lead(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="leads", db_index=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="leads"
    )

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(db_index=True)
    source = models.CharField(max_length=100)

    STATUS_CHOICE = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("converted", "Converted"),
        ("lost", "Lost"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default="new", db_index=True
    )

    value = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    converted_at = models.DateTimeField(null=True, blank=True)

    converted_to_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="source_lead",
    )

    is_archived = models.BooleanField(default=False, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"], name="unique_lead_email_per_company"
            )
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "status"]),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def clean(self):
        if self.owner and self.owner.userprofile.company != self.company:
            raise ValidationError("Owner must belong to the same company")

        if (
            self.converted_to_contact
            and self.converted_to_contact.company != self.company
        ):
            raise ValidationError("Converted contact must belong to the same company")

        if self.status == "converted" and not self.converted_to_contact:
            raise ValidationError("Converted lead must be linked to a contact")

        if self.converted_to_contact and self.status != "converted":
            raise ValidationError("Lead linked to contact must have status converted")

    def __str__(self):
        return self.name
