from django.urls import path

from .views import index, patient_lookup, tariff_preview


urlpatterns = [
    path('', index, name='imaging'),
    path('patient-lookup/', patient_lookup, name='imaging_patient_lookup'),
    path('tariff-preview/', tariff_preview, name='imaging_tariff_preview'),
]
