
from decimal import Decimal
from django.db import migrations


def create_initial_balances(apps, schema_editor):
    Currency = apps.get_model("transactions", "Currency")
    Balance = apps.get_model("transactions", "Balance")

    rub, _ = Currency.objects.get_or_create(code="RUB")
    usd, _ = Currency.objects.get_or_create(code="USD")

    Balance.objects.get_or_create(
        currency=rub,
        defaults={"amount": Decimal("10000.00")},
    )

    Balance.objects.get_or_create(
        currency=usd,
        defaults={"amount": Decimal("1000.00")},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_balances),
    ]