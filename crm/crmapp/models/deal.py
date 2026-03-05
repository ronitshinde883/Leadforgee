from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .common import Company
from .contact import Contact


class Deal(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, db_index=True, related_name="deals"
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="deals"
    )  # related_names DOUBT

    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, blank=True, null=True, related_name="deals"
    )

    title = models.CharField(max_length=100, default="")
    value = models.DecimalField(max_digits=12, decimal_places=2)

    STAGE_CHOICE = [
        ("prospecting", "Prospecting"),
        ("qualification", "Qualification"),
        ("proposal", "Proposal"),
        ("negotiation", "Negotiation"),
        ("closed-won", "Closed-won"),
        ("closed-lost", "Closed-lost"),
    ]
    stage = models.CharField(
        max_length=20, choices=STAGE_CHOICE, default="prospecting", db_index=True
    )

    expected_closed_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.contact and self.contact.company != self.company:
            raise ValidationError("Contact must belong to the same company")

        if self.owner and self.owner.userprofile.company != self.company:
            raise ValidationError("Owner must belong to the same company")
