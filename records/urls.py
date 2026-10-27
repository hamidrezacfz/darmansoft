from django.urls import path
from .views import index, patient_file
urlpatterns=[path('',index,name='records'), path('patient/<int:patient_id>/', patient_file, name='patient_file')]
