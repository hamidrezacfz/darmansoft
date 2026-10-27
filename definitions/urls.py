from django.urls import path
from .views import import_file, import_template, index, practitioners, setup
urlpatterns = [path('', index, name='definitions'), path('import/', import_file, name='definition_import'), path('import/template/<str:kind>/', import_template, name='import_template'), path('practitioners/', practitioners, name='practitioners'), path('setup/<str:kind>/', setup, name='definition_setup')]
