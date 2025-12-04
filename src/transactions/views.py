from decimal import Decimal
from django.db import transaction

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Currency, Transaction, Balance
from .serializers import TransactionSerializer
from .utils import get_balance_with_lock, apply_conversion



class BaseTransactionView(views.APIView):
    transaction_type = None

    @swagger_auto_schema(
        request_body=TransactionSerializer(),
        responses={
            200: TransactionSerializer(),
            400: '{"error": "error message"}',
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = TransactionSerializer(
            data=request.data,
            context={"transaction_type": self.transaction_type},
        )
        serializer.is_valid(raise_exception=True)

        tx: Transaction = serializer.save(transaction_type=self.transaction_type)
        self.process_transaction(tx)

        response_serializer = TransactionSerializer(tx)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def process_transaction(self, tx: Transaction):
        raise NotImplementedError


class ConversionTransactionView(BaseTransactionView):
    transaction_type = Transaction.TransactionType.CONVERSION
    
    def process_transaction(self, tx: Transaction):
        if not tx.gross_currency or not tx.exchange_rate:
            raise ValidationError(
                "gross_currency_id and exchange_rate are required for conversion."
            )

        source_balance = get_balance_with_lock(tx.gross_currency)
        target_balance = get_balance_with_lock(tx.currency)

        apply_conversion(tx, source_balance=source_balance, target_balance=target_balance)


class ServiceSpendTransactionView(BaseTransactionView):
    transaction_type = Transaction.TransactionType.SERVICE_SPEND

    def process_transaction(self, tx: Transaction):
        if tx.gross_currency:
            source_balance = get_balance_with_lock(tx.gross_currency)
            apply_conversion(tx, source_balance=source_balance, target_balance=None)
            return

        balance = get_balance_with_lock(tx.currency)
        spend_amount = tx.amount.quantize(Decimal("0.01"))

        if balance.amount < spend_amount:
            raise ValidationError(
                {"detail": "Balance is too low for service spending."}
            )

        balance.change_balance(amount=spend_amount, decrease=True)


class AccountTopUpTransactionView(BaseTransactionView):
    transaction_type = Transaction.TransactionType.ACCOUNT_TOPUP

    def process_transaction(self, tx: Transaction):
        target_balance = get_balance_with_lock(tx.currency)

        if tx.gross_currency:
            source_balance = get_balance_with_lock(tx.gross_currency)
            apply_conversion(tx, source_balance=source_balance, target_balance=target_balance)
            return

        topup_amount = tx.amount.quantize(Decimal("0.01"))

        if topup_amount <= Decimal("0"):
            raise ValidationError(
                {"sum": "sum must be greater than 0."}
            )

        target_balance.change_balance(amount=topup_amount)
        
