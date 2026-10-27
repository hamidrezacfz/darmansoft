"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from accounts import views as account_views

urlpatterns = [
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('activation/', include('licensing.urls')),
    path('', include('core.urls')),
    path('appointments/', include('appointments.urls')),
    path('billing/', include('billing.urls')),
    path('accounting/', include('accounting.urls')),
    path('definitions/', include('definitions.urls')),
    path('reception/', include('reception.urls')),
    path('beauty/', include('aesthetics.urls')),
    path('dentistry/', include('dentistry.urls')),
    path('records/', include('records.urls')),
    path('definitions/users/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
