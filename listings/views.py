from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response

from analytics.models import ListingView
from currency.models import ExchangeRate

from users.permissions import (
    IsSeller,
    IsManager,
    IsAdministrator,
)

from .models import Listing, ForbiddenWord
from .filters import ListingFilter
from .permissions import (
    IsSellerOrReadOnly,
    IsOwnerOrReadOnly,
)
from .serializers import (
    ListingSerializer,
    ForbiddenWordSerializer,
)
from .moderation import moderate_listing


class ListingListCreateView(ListCreateAPIView):
    queryset = Listing.objects.filter(
        status=Listing.Status.ACTIVE
    ).select_related(
        "seller",
        "brand",
        "model"
    ).order_by("-created_at")

    serializer_class = ListingSerializer
    permission_classes = [IsSellerOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ListingFilter

    search_fields = [
        "title",
        "description",
        "brand__name",
        "model__name",
    ]

    ordering_fields = [
        "price",
        "year",
        "mileage",
        "created_at",
    ]

    ordering = ["-created_at"]

    def perform_create(self, serializer):
        user = self.request.user

        if user.account_type == "basic" and not user.is_superuser:
            has_listing = Listing.objects.filter(
                seller=user
            ).exclude(
                status=Listing.Status.INACTIVE
            ).exists()

            if has_listing:
                raise ValidationError({
                    "detail": "Basic account allows only one listing."
                })

        rates = {
            rate.currency: rate
            for rate in ExchangeRate.objects.filter(
                currency__in=["USD", "EUR"]
            )
        }

        if not {"USD", "EUR"}.issubset(rates):
            raise ValidationError({
                "detail": "Exchange rates are not available."
            })

        listing = serializer.save(
            seller=user,
            status=Listing.Status.NEEDS_EDIT,
            original_price=serializer.validated_data["price"],
            original_currency=serializer.validated_data["currency"],
            initial_usd_uah=rates["USD"].sale,
            initial_eur_uah=rates["EUR"].sale,
            rate_recorded_at=max(
                rates["USD"].updated_at,
                rates["EUR"].updated_at
            ),
        )

        moderate_listing(listing)


class ListingDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer

    permission_classes = [
        IsSellerOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = Listing.objects.select_related(
            "seller",
            "brand",
            "model"
        )

        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser:
                return queryset

            return queryset.filter(
                Q(status=Listing.Status.ACTIVE) |
                Q(seller=user)
            )

        return queryset.filter(
            status=Listing.Status.ACTIVE
        )

    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()

        if listing.status == Listing.Status.ACTIVE:
            if (
                not request.user.is_authenticated
                or request.user.id != listing.seller_id
            ):
                ListingView.objects.create(
                    listing=listing
                )

        serializer = self.get_serializer(listing)
        return Response(serializer.data)

    def perform_update(self, serializer):
        listing = self.get_object()

        if listing.status == Listing.Status.INACTIVE:
            raise ValidationError({
                "detail": "Inactive listing cannot be edited."
            })

        listing = serializer.save()
        moderate_listing(listing, is_edit=True)


class MyListingsView(ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Listing.objects.filter(
            seller=self.request.user
        ).select_related(
            "seller",
            "brand",
            "model"
        ).order_by("-created_at")


class ForbiddenWordListCreateView(ListCreateAPIView):
    queryset = ForbiddenWord.objects.all().order_by("id")
    serializer_class = ForbiddenWordSerializer
    permission_classes = [IsAdministrator]


class ForbiddenWordDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ForbiddenWord.objects.all()
    serializer_class = ForbiddenWordSerializer
    permission_classes = [IsAdministrator]


class ManagerReviewListingsView(ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return Listing.objects.exclude(
            status=Listing.Status.ACTIVE
        ).select_related(
            "seller",
            "brand",
            "model"
        ).order_by("-created_at")


class ManagerDeleteListingView(DestroyAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return Listing.objects.exclude(
            status=Listing.Status.ACTIVE
        )
