# HealthEaseAI/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls', namespace='chat')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
]