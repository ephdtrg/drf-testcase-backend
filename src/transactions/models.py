from decimal import Decimal

from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=5, verbose_name="Код валюты", primary_key=True)

    def __str__(self):
        return f"{self.code}"

class Transaction(models.Model):
    """
    Модель транзакций клиентов.
    Описывает финансовые операции, связанные с клиентами.
    """
    class TransactionType(models.TextChoices):
        CONVERSION = "conversion", "Конвертация валюты"
        SERVICE_SPEND = "service_spend", "Покупка услуги"
        ACCOUNT_TOPUP = "account_topup", "Пополнение аккаунта"
        
    transaction_type = models.CharField(verbose_name="Тип транзакции", max_length=50, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=5, verbose_name="Сумма")
    currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,
        verbose_name="Валюта", 
        related_name="currency_transactions"
    )
    
    # Поля для конвертации валют
    gross_currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,
        verbose_name="Валюта для обмена",
        related_name="gross_currency_transactions",
        null=True,
        blank=True
    )
    exchange_rate = models.DecimalField(
        max_digits=35,
        decimal_places=16, 
        verbose_name="Обменный курс",
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    
    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
    
    def __str__(self):
        return f"{self.pk} {self.get_transaction_type_display()} {self.amount}"
    

class Balance(models.Model):
    """
    Балансы клиента.
    """
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Баланс", default=0)
    currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,
        verbose_name="Валюта", 
        related_name="balances"
    )

    def __str__(self):
        return f"{self.amount} {self.currency}"
    
    def change_balance(self, amount: Decimal, decrease: bool = False):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        
        if decrease:
            self.amount -= amount
        else:
            self.amount += amount

        self.save()
