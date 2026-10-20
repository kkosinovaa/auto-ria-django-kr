from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class AccountType(models.TextChoices):
        BASIC = "basic", "Basic"
        PREMIUM = "premium", "Premium"

    account_type = models.CharField(
        max_length=10,
        choices=AccountType.choices,
        default=AccountType.BASIC
    )

    def __str__(self):
        return self.username
