from django.urls import path
from .views import appointment_list, patient_lookup, work_schedule, delete_work_schedule
urlpatterns = [
    path('', appointment_list, name='appointment_list'),
    path('patient-lookup/', patient_lookup, name='appointment_patient_lookup'),
    path('schedule/', work_schedule, name='work_schedule'),
    path('schedule/<int:schedule_id>/delete/', delete_work_schedule, name='delete_work_schedule'),
]
