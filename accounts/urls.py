# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Signup
    path('doctor/signup/', views.doctor_signup, name='doctor_signup'),
    path('patient/signup/', views.patient_signup, name='patient_signup'),
    
    # Login
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('patient/login/', views.patient_login, name='patient_login'),
    
    # Logout
    path('logout/', views.user_logout, name='user_logout'),
    
    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),

    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
]