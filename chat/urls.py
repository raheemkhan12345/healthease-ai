from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),  # This should be your home page
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
]