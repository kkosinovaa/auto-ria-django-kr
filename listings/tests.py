from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from analytics.models import ListingView
from cars.models import CarBrand, CarModel
from currency.models import ExchangeRate
from listings.models import Listing, ForbiddenWord


class ListingAPITests(TestCase):
    def setUp(self):
        User = get_user_model()

        seller_group, _ = Group.objects.get_or_create(
            name="Seller"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.seller = User.objects.create_user(
            username="test_basic",
            password="StrongPass123!",
            account_type="basic"
        )
        self.seller.groups.add(seller_group)

        self.premium = User.objects.create_user(
            username="test_premium",
            password="StrongPass123!",
            account_type="premium"
        )
        self.premium.groups.add(seller_group)

        self.manager = User.objects.create_user(
            username="test_manager",
            email="manager@example.com",
            password="StrongPass123!"
        )
        self.manager.groups.add(manager_group)

        self.brand = CarBrand.objects.create(
            name="BMW"
        )

        self.model = CarModel.objects.create(
            brand=self.brand,
            name="X5"
        )

        ExchangeRate.objects.create(
            currency="USD",
            buy=Decimal("44.00"),
            sale=Decimal("45.00")
        )

        ExchangeRate.objects.create(
            currency="EUR",
            buy=Decimal("49.00"),
            sale=Decimal("50.00")
        )

        self.listing_data = {
            "brand": self.brand.id,
            "model": self.model.id,
            "title": "BMW X5",
            "description": "Excellent condition",
            "year": 2020,
            "mileage": 50000,
            "price": "30000.00",
            "currency": "USD",
            "region": "Lviv",
        }

        self.client = APIClient()

    def create_listing(self, seller=None, **changes):
        data = self.listing_data.copy()
        data.update(changes)

        return Listing.objects.create(
            seller=seller or self.seller,
            brand=self.brand,
            model=self.model,
            title=data["title"],
            description=data["description"],
            year=data["year"],
            mileage=data["mileage"],
            price=Decimal(data["price"]),
            currency=data["currency"],
            region=data["region"],
            status=Listing.Status.ACTIVE
        )

    def test_public_can_view_active_listings(self):
        listing = self.create_listing()

        response = self.client.get("/api/listings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], listing.id)

    def test_inactive_listing_is_hidden(self):
        listing = self.create_listing()
        listing.status = Listing.Status.INACTIVE
        listing.save()

        response = self.client.get("/api/listings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_basic_user_can_create_only_one_listing(self):
        self.client.force_authenticate(user=self.seller)

        first = self.client.post(
            "/api/listings/",
            self.listing_data,
            format="json"
        )

        second = self.client.post(
            "/api/listings/",
            {
                **self.listing_data,
                "title": "Second BMW"
            },
            format="json"
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)

    def test_premium_user_can_create_multiple_listings(self):
        self.client.force_authenticate(user=self.premium)

        first = self.client.post(
            "/api/listings/",
            self.listing_data,
            format="json"
        )

        second = self.client.post(
            "/api/listings/",
            {
                **self.listing_data,
                "title": "Another BMW"
            },
            format="json"
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)

    def test_forbidden_word_requires_editing(self):
        ForbiddenWord.objects.create(word="badword1")
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/api/listings/",
            {
                **self.listing_data,
                "description": "Contains badword1"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["status"],
            Listing.Status.NEEDS_EDIT
        )

    def test_three_failed_edits_deactivate_listing(self):
        ForbiddenWord.objects.create(word="badword1")
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/api/listings/",
            {
                **self.listing_data,
                "description": "Contains badword1"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        listing_id = response.data["id"]

        for attempt in range(1, 4):
            response = self.client.patch(
                f"/api/listings/{listing_id}/",
                {
                    "description": "Still contains badword1"
                },
                format="json"
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data["moderation_attempts"],
                attempt
            )

        self.assertEqual(
            response.data["status"],
            Listing.Status.INACTIVE
        )

    def test_listing_prices_are_converted(self):
        listing = self.create_listing()

        response = self.client.get(
            f"/api/listings/{listing.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["converted_prices"]["UAH"],
            "1350000.00"
        )

        self.assertEqual(
            response.data["converted_prices"]["USD"],
            "30000.00"
        )

    def test_search_by_brand(self):
        self.create_listing()

        response = self.client.get(
            "/api/listings/?search=BMW"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_region(self):
        self.create_listing()

        response = self.client.get(
            "/api/listings/?region=Kyiv"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_public_view_is_counted(self):
        listing = self.create_listing()

        self.client.get(
            f"/api/listings/{listing.id}/"
        )

        self.assertEqual(
            ListingView.objects.filter(
                listing=listing
            ).count(),
            1
        )

    def test_premium_analytics(self):
        listing = self.create_listing(
            seller=self.premium
        )

        ListingView.objects.create(listing=listing)
        ListingView.objects.create(listing=listing)

        self.client.force_authenticate(user=self.premium)

        response = self.client.get(
            f"/api/analytics/listings/{listing.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total_views"], 2)

    def test_basic_user_cannot_view_analytics(self):
        listing = self.create_listing()

        self.client.force_authenticate(user=self.seller)

        response = self.client.get(
            f"/api/analytics/listings/{listing.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_seller_cannot_access_manager_review(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.get(
            "/api/listings/manager/review/"
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_view_pending_listings(self):
        self.create_listing(
            description="Pending moderation"
        )

        listing = Listing.objects.first()
        listing.status = Listing.Status.NEEDS_EDIT
        listing.save()

        self.client.force_authenticate(user=self.manager)

        response = self.client.get(
            "/api/listings/manager/review/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
