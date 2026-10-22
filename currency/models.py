from django.db import models


class ExchangeRate(models.Model):
    currency = models.CharField(
        max_length=3,
        unique=True
    )
    buy = models.DecimalField(
        max_digits=12,
        decimal_places=6
    )
    sale = models.DecimalField(
        max_digits=12,
        decimal_places=6
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.currency


class ExchangeRateHistory(models.Model):
    currency = models.CharField(max_length=3)
    buy = models.DecimalField(
        max_digits=12,
        decimal_places=6
    )
    sale = models.DecimalField(
        max_digits=12,
        decimal_places=6
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.currency} - {self.recorded_at}"
