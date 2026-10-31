from django.urls import path
from . import views
urlpatterns=[path('',views.index,name='laboratory'),path('definitions/',views.definitions,name='laboratory_definitions'),path('patient-lookup/',views.patient_lookup,name='laboratory_patient_lookup'),path('order/<int:pk>/',views.order_detail,name='laboratory_order_detail'),path('order/<int:pk>/verify/',views.verify_order,name='laboratory_verify_order')]
