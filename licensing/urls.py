from django.urls import path

from .views import activation


urlpatterns = [path('', activation, name='activation')]
