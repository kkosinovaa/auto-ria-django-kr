import django_filters

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    brand = django_filters.NumberFilter(
        field_name="brand_id"
    )

    model = django_filters.NumberFilter(
        field_name="model_id"
    )

    region = django_filters.CharFilter(
        field_name="region",
        lookup_expr="iexact"
    )

    currency = django_filters.ChoiceFilter(
        choices=Listing.Currency.choices
    )

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    min_year = django_filters.NumberFilter(
        field_name="year",
        lookup_expr="gte"
    )

    max_year = django_filters.NumberFilter(
        field_name="year",
        lookup_expr="lte"
    )

    min_mileage = django_filters.NumberFilter(
        field_name="mileage",
        lookup_expr="gte"
    )

    max_mileage = django_filters.NumberFilter(
        field_name="mileage",
        lookup_expr="lte"
    )

    class Meta:
        model = Listing
        fields = [
            "brand",
            "model",
            "region",
            "currency",
            "min_price",
            "max_price",
            "min_year",
            "max_year",
            "min_mileage",
            "max_mileage",
        ]
