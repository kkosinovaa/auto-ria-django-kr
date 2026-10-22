from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from analytics.models import ListingView
from cars.models import CarBrand, CarModel
from currency.models import ExchangeRate
from currency.services import update_exchange_rates
from listings.models import Listing, ForbiddenWord
from listings.moderation import moderate_listing


class Command(BaseCommand):
    help = "Create demo users, cars and listings"

    def handle(self, *args, **options):
        rates = {
            rate.currency: rate
            for rate in ExchangeRate.objects.filter(
                currency__in=["USD", "EUR"]
            )
        }

        if not {"USD", "EUR"}.issubset(rates):
            try:
                update_exchange_rates()
            except Exception as error:
                raise CommandError(
                    f"Exchange rates are unavailable: {error}"
                ) from error

            rates = {
                rate.currency: rate
                for rate in ExchangeRate.objects.filter(
                    currency__in=["USD", "EUR"]
                )
            }

        usd_rate = rates["USD"]
        eur_rate = rates["EUR"]

        rate_recorded_at = max(
            usd_rate.updated_at,
            eur_rate.updated_at
        )

        User = get_user_model()

        seller_group, _ = Group.objects.get_or_create(
            name="Seller"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        users = [
            {
                "username": "demo_basic",
                "email": "basic@example.com",
                "account_type": "basic",
                "group": seller_group,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "demo_premium",
                "email": "premium@example.com",
                "account_type": "premium",
                "group": seller_group,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "demo_manager",
                "email": "manager@example.com",
                "account_type": "basic",
                "group": manager_group,
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "demo_admin",
                "email": "admin@example.com",
                "account_type": "premium",
                "group": None,
                "is_staff": True,
                "is_superuser": True,
            },
        ]

        created_users = {}

        for data in users:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "account_type": data["account_type"],
                    "is_staff": data["is_staff"],
                    "is_superuser": data["is_superuser"],
                }
            )

            if created:
                user.set_password("DemoPass123!")
                user.save()

            if data["group"] is not None:
                user.groups.add(data["group"])

            created_users[user.username] = user

        bmw, _ = CarBrand.objects.get_or_create(
            name="BMW"
        )

        audi, _ = CarBrand.objects.get_or_create(
            name="Audi"
        )

        toyota, _ = CarBrand.objects.get_or_create(
            name="Toyota"
        )

        x5, _ = CarModel.objects.get_or_create(
            brand=bmw,
            name="X5"
        )

        m5, _ = CarModel.objects.get_or_create(
            brand=bmw,
            name="M5"
        )

        a6, _ = CarModel.objects.get_or_create(
            brand=audi,
            name="A6"
        )

        camry, _ = CarModel.objects.get_or_create(
            brand=toyota,
            name="Camry"
        )

        ForbiddenWord.objects.get_or_create(
            word="badword1"
        )

        demo_listings = [
            {
                "seller": created_users["demo_basic"],
                "brand": audi,
                "model": a6,
                "title": "Audi A6 2017",
                "description": "Comfortable family car",
                "year": 2017,
                "mileage": 150000,
                "price": Decimal("18000.00"),
                "currency": "USD",
                "region": "Lviv",
            },
            {
                "seller": created_users["demo_premium"],
                "brand": bmw,
                "model": x5,
                "title": "BMW X5 2020",
                "description": "Excellent condition",
                "year": 2020,
                "mileage": 65000,
                "price": Decimal("45000.00"),
                "currency": "USD",
                "region": "Lviv",
            },
            {
                "seller": created_users["demo_premium"],
                "brand": bmw,
                "model": m5,
                "title": "BMW M5 2021",
                "description": "Powerful sports sedan",
                "year": 2021,
                "mileage": 30000,
                "price": Decimal("65000.00"),
                "currency": "EUR",
                "region": "Kyiv",
            },
            {
                "seller": created_users["demo_premium"],
                "brand": toyota,
                "model": camry,
                "title": "Toyota Camry 2019",
                "description": "Reliable car in great condition",
                "year": 2019,
                "mileage": 90000,
                "price": Decimal("950000.00"),
                "currency": "UAH",
                "region": "Odesa",
            },
            {
                "seller": created_users["demo_premium"],
                "brand": bmw,
                "model": x5,
                "title": "BMW X5 Moderation Test",
                "description": "Contains badword1",
                "year": 2018,
                "mileage": 110000,
                "price": Decimal("25000.00"),
                "currency": "USD",
                "region": "Lviv",
            },
        ]

        for data in demo_listings:
            listing, created = Listing.objects.get_or_create(
                seller=data["seller"],
                title=data["title"],
                defaults={
                    "brand": data["brand"],
                    "model": data["model"],
                    "description": data["description"],
                    "year": data["year"],
                    "mileage": data["mileage"],
                    "price": data["price"],
                    "currency": data["currency"],
                    "region": data["region"],
                    "contact_email": data["seller"].email,
                    "original_price": data["price"],
                    "original_currency": data["currency"],
                    "initial_usd_uah": usd_rate.sale,
                    "initial_eur_uah": eur_rate.sale,
                    "rate_recorded_at": rate_recorded_at,
                    "status": Listing.Status.NEEDS_EDIT,
                }
            )

            if created:
                moderate_listing(listing)
            elif not listing.contact_email:
                listing.contact_email = data["seller"].email
                listing.save(update_fields=["contact_email"])

        premium_listing = Listing.objects.get(
            seller=created_users["demo_premium"],
            title="BMW X5 2020"
        )

        if not ListingView.objects.filter(
            listing=premium_listing
        ).exists():
            ListingView.objects.bulk_create([
                ListingView(listing=premium_listing)
                for _ in range(5)
            ])

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data created successfully."
            )
        )

        self.stdout.write(
            "Users: demo_basic, demo_premium, "
            "demo_manager, demo_admin"
        )

        self.stdout.write(
            "Password: DemoPass123!"
        )

        self.stdout.write(
            f"Brands: {CarBrand.objects.count()}"
        )

        self.stdout.write(
            f"Listings: {Listing.objects.count()}"
        )
