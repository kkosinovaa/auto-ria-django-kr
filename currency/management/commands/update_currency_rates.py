from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from currency.services import update_exchange_rates


class Command(BaseCommand):
    help = "Update USD and EUR exchange rates from PrivatBank"

    def handle(self, *args, **options):
        try:
            rates = update_exchange_rates()
        except Exception as error:
            raise CommandError(str(error)) from error

        for currency, values in rates.items():
            self.stdout.write(
                self.style.SUCCESS(
                    f"{currency}: "
                    f"buy={values['buy']}, "
                    f"sale={values['sale']}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Exchange rates updated successfully."
            )
        )
