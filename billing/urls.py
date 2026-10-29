from django.urls import path
from .views import payment_list, report, payment_receipt, referral_preview
urlpatterns = [path('', payment_list, name='payment_list'), path('referral-preview/', referral_preview, name='referral_preview'), path('report/', report, name='billing_report'), path('receipt/<int:payment_id>/', payment_receipt, name='payment_receipt')]
