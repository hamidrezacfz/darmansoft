from django.urls import path
from .views import admission, report

urlpatterns = [path('', admission, name='dentistry'), path('admission/', admission, name='dental_admission'), path('report/', report, name='dental_report')]
