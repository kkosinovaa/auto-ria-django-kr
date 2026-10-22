from django.conf import settings
from django.db import models


class Listing(models.Model):
    class Currency(models.TextChoices):
        USD = "USD", "USD"
        EUR = "EUR", "EUR"
        UAH = "UAH", "UAH"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        NEEDS_EDIT = "needs_edit", "Needs edit"
        INACTIVE = "inactive", "Inactive"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings"
    )

    brand = models.ForeignKey(
        "cars.CarBrand",
        on_delete=models.PROTECT
    )

    model = models.ForeignKey(
        "cars.CarModel",
        on_delete=models.PROTECT
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices
    )

    region = models.CharField(max_length=100)

    contact_email = models.EmailField(
        blank=True
    )

    original_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True
    )

    original_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        null=True,
        blank=True
    )

    initial_usd_uah = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )

    initial_eur_uah = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True
    )

    rate_recorded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.NEEDS_EDIT
    )

    moderation_attempts = models.PositiveSmallIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class ForbiddenWord(models.Model):
    word = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.word
