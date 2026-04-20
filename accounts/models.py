from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.business_name
