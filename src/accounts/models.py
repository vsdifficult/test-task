from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
