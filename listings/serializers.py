from datetime import date

from rest_framework import serializers

from currency.models import ExchangeRate
from currency.services import convert_price

from .models import Listing, ForbiddenWord


class ListingSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True
    )

    model_name = serializers.CharField(
        source="model.name",
        read_only=True
    )

    converted_prices = serializers.SerializerMethodField()
    rates_used = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            "id",
            "seller",
            "brand",
            "brand_name",
            "model",
            "model_name",
            "title",
            "description",
            "year",
            "mileage",
            "price",
            "currency",
            "region",
            "contact_email",
            "original_price",
            "original_currency",
            "initial_usd_uah",
            "initial_eur_uah",
            "rate_recorded_at",
            "converted_prices",
            "rates_used",
            "status",
            "moderation_attempts",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "seller",
            "original_price",
            "original_currency",
            "initial_usd_uah",
            "initial_eur_uah",
            "rate_recorded_at",
            "status",
            "moderation_attempts",
            "created_at",
            "updated_at",
        )

    def get_rates(self):
        if "_exchange_rates" not in self.context:
            self.context["_exchange_rates"] = {
                rate.currency: rate
                for rate in ExchangeRate.objects.all()
            }

        return self.context["_exchange_rates"]

    def get_converted_prices(self, obj):
        rates = self.get_rates()

        if not {"USD", "EUR"}.issubset(rates):
            return None

        return convert_price(
            obj.price,
            obj.currency,
            rates
        )

    def get_rates_used(self, obj):
        rates = self.get_rates()

        if not {"USD", "EUR"}.issubset(rates):
            return None

        return {
            "source": "PrivatBank",
            "rate_type": "sale",
            "USD_UAH": str(rates["USD"].sale),
            "EUR_UAH": str(rates["EUR"].sale),
            "updated_at": max(
                rates["USD"].updated_at,
                rates["EUR"].updated_at
            ).isoformat(),
        }

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )

        return value

    def validate_year(self, value):
        if value < 1886 or value > date.today().year + 1:
            raise serializers.ValidationError(
                "Invalid manufacturing year."
            )

        return value

    def validate(self, attrs):
        brand = attrs.get(
            "brand",
            getattr(self.instance, "brand", None)
        )

        model = attrs.get(
            "model",
            getattr(self.instance, "model", None)
        )

        if brand and model and model.brand_id != brand.id:
            raise serializers.ValidationError({
                "model": "This model does not belong to the selected brand."
            })

        return attrs


class ForbiddenWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenWord
        fields = (
            "id",
            "word",
        )

    def validate_word(self, value):
        word = value.strip().lower()

        if not word:
            raise serializers.ValidationError(
                "Word cannot be empty."
            )

        queryset = ForbiddenWord.objects.filter(
            word__iexact=word
        )

        if self.instance is not None:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "This word already exists."
            )

        return word
