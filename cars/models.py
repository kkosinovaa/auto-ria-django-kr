from django.db import models
from django.conf import settings

class CarBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(
        CarBrand,
        on_delete=models.CASCADE,
        related_name="models"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "name"],
                name="unique_car_model_per_brand"
            )
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class CarCatalogRequest(models.Model):
    class RequestType(models.TextChoices):
        BRAND = "brand", "Brand"
        MODEL = "model", "Model"

    request_type = models.CharField(
        max_length=10,
        choices=RequestType.choices
    )
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(
        CarBrand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
