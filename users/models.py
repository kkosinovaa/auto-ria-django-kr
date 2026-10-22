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

class PremiumPurchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="premium_purchases"
    )
    payment_status = models.CharField(
        max_length=20,
        default="mock_success"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Premium purchase by {self.user.username}"
