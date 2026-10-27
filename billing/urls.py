from django.urls import path
from .views import payment_list, report, payment_receipt
urlpatterns = [path('', payment_list, name='payment_list'), path('report/', report, name='billing_report'), path('receipt/<int:payment_id>/', payment_receipt, name='payment_receipt')]
