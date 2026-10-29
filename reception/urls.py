from django.urls import path
from .views import index, tariff_preview, patient_lookup, practitioner_lookup, service_lookup, edit_open_admission
urlpatterns = [path('', index, name='reception'), path('edit/<str:tracking_code>/', edit_open_admission, name='edit_open_admission'), path('tariff-preview/', tariff_preview, name='tariff_preview'), path('patient-lookup/', patient_lookup, name='patient_lookup'), path('practitioner-lookup/', practitioner_lookup, name='practitioner_lookup'), path('service-lookup/', service_lookup, name='service_lookup')]
