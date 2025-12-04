
# Тестовое задание на DRF

## Реализованный функционал

### Модели
- Transaction - полностью из задания
- Balance - валюта перенесена в отдельную модель Currency
- Currency - отдельная модель для хранения списка валют

Создание первичных моделей происходит в миграциях

### Эндпоинты

Реализован базовый класс BaseTransactionView, в котором происходит:
1. Обработка по сериалайзеру TransactionSerializer
2. Сохранение записи о транзакции в модель Transaction
3. Дальнейшая работа эндпоинта осуществляется через вызов self.process_transaction (реализованы в наследуемых классах)

Все эндпоинты, указанные в пункте 5 задания - реализованы
- /transactions/conversion/ - отвечает за конвертацию (класс ConversionTransactionView)
- /transactions/service-spend/ - отвечает за покупку услуги (класс ServiceSpendTransactionView)
- /transactions/account-topup/ - отвечает за пополнение аккаунта (класс AccountTopUpTransactionView)


### Валидация

Происходит в сериалайзере TransactionSerializer, реализованы:
- проеверка минимальных значений
- наличия необходимых полей для конкретных эндпоинтов

### Обработка запроса

Тело запроса для всех эндпоинтов имеет единую структуру согласно заданию

```
{
"sum": "1.11414",
"currency_id": "USD",
"gross_currency_id": "RUB",
"exchange_rate": "85.0"
}
```

### Прочее

Тест-кейсы реализовать не успел, но добавил в проект swagger, доступен по эндпоинту:
http://127.0.0.1:8000/api/swagger/


- БД используется sqlite
- requirements.txt прилагаю (сам использую `uv`).

Для запуска проекта:
```
uv venv venv 
source venv/bin/activate
python3 manage.py migrate
python3 manage.py runserver
```
