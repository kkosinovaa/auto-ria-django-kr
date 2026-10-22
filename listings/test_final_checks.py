from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from cars.models import CarBrand, CarModel
from currency.models import ExchangeRate
from listings.models import Listing


class FinalChecksTests(TestCase):
    def setUp(self):
        User = get_user_model()

        seller_group, _ = Group.objects.get_or_create(name="Seller")
        manager_group, _ = Group.objects.get_or_create(name="Manager")

        self.seller = User.objects.create_user(
            username="final_seller",
            password="StrongPass123!",
            account_type="premium"
        )
        self.seller.groups.add(seller_group)

        self.manager = User.objects.create_user(
            username="final_manager",
            password="StrongPass123!"
        )
        self.manager.groups.add(manager_group)

        self.brand = CarBrand.objects.create(name="BMW")
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

        self.client = APIClient()

    def create_listing(self, status):
        return Listing.objects.create(
            seller=self.seller,
            brand=self.brand,
            model=self.model,
            title="BMW X5 Test",
            description="Test car",
            year=2020,
            mileage=50000,
            price=Decimal("30000.00"),
            currency="USD",
            region="Lviv",
            status=status
        )

    def test_manager_cannot_delete_active_listing(self):
        listing = self.create_listing(Listing.Status.ACTIVE)

        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(
            f"/api/listings/manager/{listing.id}/delete/"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Listing.objects.filter(pk=listing.id).exists()
        )

    def test_manager_can_delete_invalid_listing(self):
        listing = self.create_listing(Listing.Status.NEEDS_EDIT)

        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(
            f"/api/listings/manager/{listing.id}/delete/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Listing.objects.filter(pk=listing.id).exists()
        )

    def test_original_price_and_rates_are_saved(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/api/listings/",
            {
                "brand": self.brand.id,
                "model": self.model.id,
                "title": "BMW X5 New",
                "description": "Excellent condition",
                "year": 2022,
                "mileage": 35000,
                "price": "55000.00",
                "currency": "USD",
                "region": "Lviv"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        listing = Listing.objects.get(pk=response.data["id"])

        self.assertEqual(
            listing.original_price,
            Decimal("55000.00")
        )
        self.assertEqual(listing.original_currency, "USD")
        self.assertEqual(
            listing.initial_usd_uah,
            Decimal("45.00")
        )
        self.assertEqual(
            listing.initial_eur_uah,
            Decimal("50.00")
        )
        self.assertIsNotNone(listing.rate_recorded_at)
