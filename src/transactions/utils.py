from decimal import Decimal

from rest_framework.exceptions import ValidationError

from .models import Balance, Transaction


def get_balance_with_lock(currency):
    try:
        return Balance.objects.select_for_update().get(currency=currency)
    except Balance.DoesNotExist:
        raise ValidationError(
            {"detail": f"Balance for currency {currency.code} does not exist."}
        )
    

def apply_conversion(tx: Transaction, source_balance: Balance, target_balance: Balance | None):
    if not tx.exchange_rate:
        raise ValidationError({"exchange_rate": "exchange_rate is required for conversion."})

    gross_amount = (tx.amount * tx.exchange_rate).quantize(Decimal("0.01"))

    if gross_amount <= Decimal("0"):
        raise ValidationError({"exchange_rate": "Resulting converted amount must be greater than 0."})

    if source_balance.amount < gross_amount:
        raise ValidationError(
            {"detail": "Balance is too low for conversion."}
        )

    source_balance.change_balance(amount=gross_amount, decrease=True)

    if target_balance is not None:
        target_balance.change_balance(amount=tx.amount)