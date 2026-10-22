from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from currency.models import ExchangeRate
from listings.models import Listing
from .models import ListingView


class ListingAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        if user.account_type != "premium" and not user.is_superuser:
            raise PermissionDenied(
                "Analytics is available only for Premium accounts."
            )

        listing = get_object_or_404(Listing, pk=pk)

        if listing.seller_id != user.id and not user.is_superuser:
            raise PermissionDenied(
                "You can only view analytics for your own listings."
            )

        now = timezone.now()
        views = ListingView.objects.filter(listing=listing)

        rates = {
            rate.currency: rate.sale
            for rate in ExchangeRate.objects.all()
        }

        if "USD" not in rates or "EUR" not in rates:
            raise ValidationError("Exchange rates are not available.")

        similar_listings = Listing.objects.filter(
            brand=listing.brand,
            model=listing.model,
            status=Listing.Status.ACTIVE
        )

        def average_price(queryset):
            total = Decimal("0")
            count = 0

            for car in queryset:
                if car.currency == "UAH":
                    price_uah = car.price
                else:
                    price_uah = car.price * rates[car.currency]

                total += price_uah
                count += 1

            if count == 0:
                return None

            average = total / count

            return str(
                average.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP
                )
            )

        regional_listings = similar_listings.filter(
            region__iexact=listing.region
        )

        return Response({
            "listing_id": listing.id,
            "title": listing.title,
            "total_views": views.count(),
            "views_today": views.filter(
                viewed_at__gte=now - timedelta(days=1)
            ).count(),
            "views_week": views.filter(
                viewed_at__gte=now - timedelta(days=7)
            ).count(),
            "views_month": views.filter(
                viewed_at__gte=now - timedelta(days=30)
            ).count(),
            "region": listing.region,
            "average_price_region_uah": average_price(regional_listings),
            "average_price_ukraine_uah": average_price(similar_listings)
        })
