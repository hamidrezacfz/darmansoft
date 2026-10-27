from django.urls import path
from .views import backups, home

urlpatterns = [path('', home, name='home'), path('backups/', backups, name='backups')]
