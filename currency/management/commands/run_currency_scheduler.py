import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone

from currency.models import ExchangeRateHistory


class Command(BaseCommand):
    help = "Automatically update exchange rates once per day"

    def handle(self, *args, **options):
        self.stdout.write("Currency scheduler started.")

        while True:
            try:
                close_old_connections()

                today = timezone.localdate()

                currencies_updated = all(
                    ExchangeRateHistory.objects.filter(
                        currency=currency,
                        recorded_at__date=today
                    ).exists()
                    for currency in ("USD", "EUR")
                )

                if not currencies_updated:
                    self.stdout.write(
                        "Updating daily exchange rates..."
                    )

                    call_command("update_currency_rates")

                    self.stdout.write(
                        self.style.SUCCESS(
                            "Daily exchange rates updated."
                        )
                    )

            except KeyboardInterrupt:
                self.stdout.write("Currency scheduler stopped.")
                break

            except Exception as error:
                self.stderr.write(
                    f"Currency update failed: {error}"
                )

            finally:
                close_old_connections()

            time.sleep(300)
