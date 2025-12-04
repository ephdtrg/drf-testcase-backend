from django.urls import path

from .views import ConversionTransactionView, ServiceSpendTransactionView, AccountTopUpTransactionView

urlpatterns = [
    path('conversion/', ConversionTransactionView.as_view()),
    path('service-spend/', ServiceSpendTransactionView.as_view()),
    path('account-topup/', AccountTopUpTransactionView.as_view()),
]