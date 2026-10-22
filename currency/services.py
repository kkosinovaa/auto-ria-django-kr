from decimal import Decimal, ROUND_HALF_UP

import requests
from django.db import transaction

from .models import ExchangeRate, ExchangeRateHistory


PRIVATBANK_URL = (
    "https://api.privatbank.ua/p24api/pubinfo"
    "?json&exchange&coursid=5"
)


def update_exchange_rates():
    response = requests.get(
        PRIVATBANK_URL,
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    rates = {}

    for item in data:
        currency = item.get("ccy")

        if (
            currency in ("USD", "EUR")
            and item.get("base_ccy") == "UAH"
        ):
            buy = Decimal(str(item["buy"]))
            sale = Decimal(str(item["sale"]))

            if buy <= 0 or sale <= 0:
                raise ValueError("Invalid exchange rate")

            rates[currency] = {
                "buy": buy,
                "sale": sale,
            }

    if set(rates) != {"USD", "EUR"}:
        raise ValueError(
            "USD or EUR exchange rate is missing"
        )

    with transaction.atomic():
        for currency, values in rates.items():
            ExchangeRate.objects.update_or_create(
                currency=currency,
                defaults=values
            )

            ExchangeRateHistory.objects.create(
                currency=currency,
                buy=values["buy"],
                sale=values["sale"]
            )

    return rates


def convert_price(price, currency, rates):
    if currency == "UAH":
        price_uah = price
    else:
        price_uah = price * rates[currency].sale

    result = {}

    for code in ("UAH", "USD", "EUR"):
        if code == "UAH":
            value = price_uah
        else:
            value = price_uah / rates[code].sale

        result[code] = str(
            value.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        )

    return result
