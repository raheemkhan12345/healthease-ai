from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [

    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('login/patient/', views.patient_login, name='patient_login'),
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard/Profile URLs
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),

    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),  # Make sure this exists
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    
    
]