from decimal import Decimal
from rest_framework import serializers

from .models import Currency, Transaction, Balance


class TransactionSerializer(serializers.ModelSerializer):
    sum = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        source="amount",
    )
    currency_id = serializers.SlugRelatedField(
        slug_field="code",
        source="currency",
        queryset=Currency.objects.all(),
    )
    gross_currency_id = serializers.SlugRelatedField(
        slug_field="code",
        source="gross_currency",
        queryset=Currency.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Transaction
        fields = (
            "id",
            "transaction_type",
            "sum",
            "currency_id",
            "gross_currency_id",
            "exchange_rate",
            "created_at",
        )
        read_only_fields = ("id", "transaction_type", "created_at")

    def _validate_tx_currencies(self, tx_type, currency, gross_currency):
        restricted_types = {
            Transaction.TransactionType.SERVICE_SPEND,
            Transaction.TransactionType.ACCOUNT_TOPUP,
        }

        allowed = {"RUB", "USD"}
        errors = {}

        if currency and currency.code.upper() not in allowed:
            errors["currency_id"] = "Only RUB and USD are supported."

        if gross_currency and gross_currency.code.upper() not in allowed:
            errors["gross_currency_id"] = "Only RUB and USD are supported."

        if tx_type in restricted_types:
            if currency and currency.code.upper() != "RUB":
                errors["currency_id"] = "currency_id must be RUB."

            if gross_currency is not None and gross_currency.code.upper() != "USD":
                errors["gross_currency_id"] = "gross_currency_id must be USD."

        if errors:
            raise serializers.ValidationError(errors)

    def validate(self, attrs):
        tx_type = self.context.get("transaction_type")

        amount = attrs.get("amount")
        currency = attrs.get("currency")
        gross_currency = attrs.get("gross_currency")
        rate = attrs.get("exchange_rate")

        if amount is None or amount <= Decimal("0"):
            raise serializers.ValidationError(
                {"sum": "sum must be greater than 0."}
            )

        if rate is not None and rate <= Decimal("0"):
            raise serializers.ValidationError(
                {"exchange_rate": "exchange_rate must be greater than 0."}
            )

        self._validate_tx_currencies(tx_type, currency, gross_currency)

        has_gross = gross_currency is not None
        has_rate = rate is not None

        if has_gross != has_rate:
            raise serializers.ValidationError(
                "gross_currency_id and exchange_rate must be provided together."
            )

        if tx_type == Transaction.TransactionType.CONVERSION:
            if not has_gross:
                raise serializers.ValidationError(
                    "gross_currency_id and exchange_rate are required for conversion."
                )
            if currency == gross_currency:
                raise serializers.ValidationError(
                    {"gross_currency_id": "currency_id and gross_currency_id must be different for conversion."}
                )

        return attrs
    

class BalanceSerializer(serializers.ModelSerializer):
    currency_id = serializers.SlugRelatedField(
        slug_field="code",
        source="currency",
        read_only=True
    )

    class Meta:
        model = Balance
        fields = ("id", "amount", "currency_id")


