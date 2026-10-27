from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='accounting_dashboard'),
    path('report/', views.financial_report, name='financial_report'),
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/report/', views.inventory_report, name='inventory_report'),
    path('practitioner-shares/', views.practitioner_shares, name='practitioner_shares'),
]
