from django.urls import path
from .views import admission, index, report

urlpatterns = [path('', admission, name='dentistry'), path('setup/', index, name='dental_setup'), path('admission/', admission, name='dental_admission'), path('report/', report, name='dental_report')]
