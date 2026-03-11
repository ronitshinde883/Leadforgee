from django.db import models
from django.contrib.auth.models import User

from .common import Company


class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.URLField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, db_index=True, related_name="users")
    is_emailverified = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("member", "Member"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member", db_index=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.user.username

# REMOVED FIELDS
# fullname=models.CharField(max_length=100)
# username=models.CharField(max_length=100)
# email=models.EmailField(unique=True)
# is_active=models.BooleanField(default=True)
