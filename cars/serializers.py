from rest_framework import serializers
from .models import CarBrand, CarModel
from .models import CarCatalogRequest


class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ("id", "name")


class CarModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(
        source="brand.name",
        read_only=True
    )

    class Meta:
        model = CarModel
        fields = ("id", "name", "brand", "brand_name")


class CarCatalogRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarCatalogRequest
        fields = (
            "id",
            "request_type",
            "name",
            "brand",
            "created_by",
            "created_at",
        )
        read_only_fields = ("id", "created_by", "created_at")

    def validate(self, attrs):
        request_type = attrs.get("request_type")
        brand = attrs.get("brand")

        if request_type == "model" and not brand:
            raise serializers.ValidationError(
                "Choose a brand for the requested model."
            )

        if request_type == "brand" and brand:
            raise serializers.ValidationError(
                "A brand request must not specify a brand."
            )

        return attrs
