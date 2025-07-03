# HealthEaseAI/urls.py
from django.contrib import admin
from django.urls import path, include
from appointments import views as appointment_views  # Correct import for home view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', appointment_views.home, name='home'),  # ✅ Make sure this line exists
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    
]

# Media config
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
